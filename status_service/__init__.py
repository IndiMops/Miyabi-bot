"""
Standalone status service for Miyabi Bot.

Receives authenticated heartbeats, decides the service state from heartbeat
freshness and keeps a single Discord status message up to date through a
webhook. Run it as a separate process: `python -m status_service`.
"""
