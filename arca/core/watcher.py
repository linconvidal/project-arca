"""
File system watcher for Arca

This module provides functionality to monitor the content directory for changes
and trigger appropriate actions when files are created, modified, or deleted.
"""
import os
import time
from pathlib import Path
from threading import Thread, Event
import logging
from typing import Callable, Dict, Set, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)

class ArcaEventHandler(FileSystemEventHandler):
    """
    Custom event handler for file system events in the Arca content directory.
    Filters events and calls appropriate callbacks for relevant file changes.
    """
    
    def __init__(self, 
                 file_extensions: Set[str], 
                 on_created: Callable[[Path], None],
                 on_modified: Callable[[Path], None],
                 on_deleted: Callable[[Path], None],
                 debounce_time: float = 0.5):
        """
        Initialize the event handler with callbacks for different event types.
        
        Args:
            file_extensions: Set of file extensions to monitor (e.g., {'.md', '.yaml'})
            on_created: Callback function when a file is created
            on_modified: Callback function when a file is modified
            on_deleted: Callback function when a file is deleted
            debounce_time: Time in seconds to wait before processing an event
                          (to avoid duplicate events)
        """
        self.file_extensions = file_extensions
        self.on_created = on_created
        self.on_modified = on_modified
        self.on_deleted = on_deleted
        self.debounce_time = debounce_time
        
        # Debounce mechanism: track last event time per path
        self.last_events: Dict[str, float] = {}
        
        # Track files being processed to avoid reprocessing
        self.processing: Set[str] = set()
    
    def _should_process_file(self, path: str) -> bool:
        """
        Check if a file should be processed based on its extension and
        whether it's a temporary file.
        
        Args:
            path: Path to the file
            
        Returns:
            bool: True if the file should be processed, False otherwise
        """
        # Skip temporary files and files with non-matching extensions
        _, ext = os.path.splitext(path)
        
        # Skip hidden files and directories
        if os.path.basename(path).startswith('.'):
            return False
            
        # Skip temporary files (common patterns)
        if path.endswith('~') or path.endswith('.swp') or path.endswith('.tmp'):
            return False
            
        return ext.lower() in self.file_extensions
    
    def _debounce(self, event_path: str) -> bool:
        """
        Implement debounce mechanism to avoid processing the same file multiple times
        in quick succession.
        
        Args:
            event_path: Path to the file that triggered the event
            
        Returns:
            bool: True if the event should be processed, False if it should be ignored
        """
        current_time = time.time()
        
        # If the file is currently being processed, ignore this event
        if event_path in self.processing:
            return False
            
        # Check if we've seen this file recently
        if event_path in self.last_events:
            last_time = self.last_events[event_path]
            if current_time - last_time < self.debounce_time:
                # Update the timestamp and ignore this event
                self.last_events[event_path] = current_time
                return False
        
        # Update the timestamp and process this event
        self.last_events[event_path] = current_time
        return True
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events"""
        if not event.is_directory and self._should_process_file(event.src_path):
            if self._debounce(event.src_path):
                logger.debug(f"File created: {event.src_path}")
                try:
                    self.processing.add(event.src_path)
                    self.on_created(Path(event.src_path))
                finally:
                    self.processing.remove(event.src_path)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events"""
        if not event.is_directory and self._should_process_file(event.src_path):
            if self._debounce(event.src_path):
                logger.debug(f"File modified: {event.src_path}")
                try:
                    self.processing.add(event.src_path)
                    self.on_modified(Path(event.src_path))
                finally:
                    self.processing.remove(event.src_path)
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events"""
        if not event.is_directory and self._should_process_file(event.src_path):
            if self._debounce(event.src_path):
                logger.debug(f"File deleted: {event.src_path}")
                try:
                    self.processing.add(event.src_path)
                    self.on_deleted(Path(event.src_path))
                finally:
                    self.processing.remove(event.src_path)
    
    def on_moved(self, event: FileSystemEvent):
        """
        Handle file move events (treat as delete + create)
        """
        # Handle source file (deletion)
        if not event.is_directory and self._should_process_file(event.src_path):
            if self._debounce(event.src_path):
                logger.debug(f"File moved from: {event.src_path}")
                try:
                    self.processing.add(event.src_path)
                    self.on_deleted(Path(event.src_path))
                finally:
                    self.processing.remove(event.src_path)
        
        # Handle destination file (creation)
        if not event.is_directory and self._should_process_file(event.dest_path):
            if self._debounce(event.dest_path):
                logger.debug(f"File moved to: {event.dest_path}")
                try:
                    self.processing.add(event.dest_path)
                    self.on_created(Path(event.dest_path))
                finally:
                    self.processing.remove(event.dest_path)


class ContentWatcher:
    """
    Watches a content directory for changes and triggers callbacks when files
    are created, modified, or deleted.
    """
    
    def __init__(self, 
                 content_dir: Path,
                 file_extensions: Set[str] = {'.md', '.yaml', '.yml'},
                 debounce_time: float = 0.5):
        """
        Initialize the content watcher.
        
        Args:
            content_dir: Path to the content directory to watch
            file_extensions: Set of file extensions to monitor
            debounce_time: Time in seconds to wait before processing an event
        """
        self.content_dir = Path(content_dir)
        self.file_extensions = {ext.lower() if not ext.startswith('.') else ext for ext in file_extensions}
        self.debounce_time = debounce_time
        self.observer = None
        self.stop_event = Event()
        self._callbacks = {
            'created': [],
            'modified': [],
            'deleted': []
        }
    
    def on_created(self, callback: Callable[[Path], None]):
        """Register a callback for file creation events"""
        self._callbacks['created'].append(callback)
        return self
    
    def on_modified(self, callback: Callable[[Path], None]):
        """Register a callback for file modification events"""
        self._callbacks['modified'].append(callback)
        return self
    
    def on_deleted(self, callback: Callable[[Path], None]):
        """Register a callback for file deletion events"""
        self._callbacks['deleted'].append(callback)
        return self
    
    def _handle_created(self, path: Path):
        """Call all registered creation callbacks"""
        for callback in self._callbacks['created']:
            try:
                callback(path)
            except Exception as e:
                logger.error(f"Error in creation callback for {path}: {e}")
    
    def _handle_modified(self, path: Path):
        """Call all registered modification callbacks"""
        for callback in self._callbacks['modified']:
            try:
                callback(path)
            except Exception as e:
                logger.error(f"Error in modification callback for {path}: {e}")
    
    def _handle_deleted(self, path: Path):
        """Call all registered deletion callbacks"""
        for callback in self._callbacks['deleted']:
            try:
                callback(path)
            except Exception as e:
                logger.error(f"Error in deletion callback for {path}: {e}")
    
    def start(self):
        """Start watching the content directory"""
        if self.observer:
            logger.warning("Watcher is already running")
            return
        
        # Create the content directory if it doesn't exist
        if not self.content_dir.exists():
            self.content_dir.mkdir(parents=True)
            logger.info(f"Created content directory: {self.content_dir}")
        
        # Create and configure the event handler
        event_handler = ArcaEventHandler(
            file_extensions=self.file_extensions,
            on_created=self._handle_created,
            on_modified=self._handle_modified,
            on_deleted=self._handle_deleted,
            debounce_time=self.debounce_time
        )
        
        # Create and start the observer
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.content_dir), recursive=True)
        self.observer.start()
        
        logger.info(f"Started watching directory: {self.content_dir}")
        logger.info(f"Monitoring file extensions: {self.file_extensions}")
    
    def stop(self):
        """Stop watching the content directory"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Stopped watching content directory")
    
    def scan_existing_files(self):
        """
        Scan all existing files in the content directory and trigger creation callbacks.
        This is useful for initial loading of content.
        """
        logger.info(f"Scanning existing files in {self.content_dir}")
        
        for ext in self.file_extensions:
            pattern = f"*{ext}"
            for file_path in self.content_dir.glob(f"**/{pattern}"):
                if file_path.is_file():
                    logger.debug(f"Found existing file: {file_path}")
                    self._handle_created(file_path)
        
        logger.info("Completed initial scan of existing files") 