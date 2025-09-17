"""
Socket.IO event handlers for real-time communication.
"""
from flask import current_app
from flask_login import current_user
from .extensions import sio, mongo
from .models.user import User
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Dictionary to keep track of connected users
connected_users = {}

@sio.event
def connect(sid, environ, auth=None):
    """Handle new socket connection."""
    logger.info(f"Client connected: {sid}")
    
    # You can add authentication logic here if needed
    # For example, verify a JWT token from the auth parameter
    
    return {'status': 'connected'}

@sio.event
def identify(sid, data):
    """Identify a connected user."""
    if not data or 'user_id' not in data:
        return {'status': 'error', 'message': 'User ID is required'}
    
    user_id = data['user_id']
    
    # Store the socket ID with the user ID
    connected_users[user_id] = sid
    logger.info(f"User {user_id} identified with socket {sid}")
    
    return {'status': 'identified'}

@sio.event
def join_room(sid, data):
    """Join a room."""
    if not data or 'room' not in data:
        return {'status': 'error', 'message': 'Room is required'}
    
    room = data['room']
    sio.enter_room(sid, room)
    logger.info(f"Socket {sid} joined room {room}")
    
    return {'status': 'joined', 'room': room}

@sio.event
def leave_room(sid, data):
    """Leave a room."""
    if not data or 'room' not in data:
        return {'status': 'error', 'message': 'Room is required'}
    
    room = data['room']
    sio.leave_room(sid, room)
    logger.info(f"Socket {sid} left room {room}")
    
    return {'status': 'left', 'room': room}

@sio.event
def send_message(sid, data):
    """Send a message to a room or user."""
    if not data or 'message' not in data:
        return {'status': 'error', 'message': 'Message is required'}
    
    message = data['message']
    room = data.get('room')
    recipient_id = data.get('recipient_id')
    
    # Get the sender's user ID from the session
    sender_id = None
    for user_id, socket_id in connected_users.items():
        if socket_id == sid:
            sender_id = user_id
            break
    
    if not sender_id:
        return {'status': 'error', 'message': 'User not identified'}
    
    # Get the sender's user data
    sender = User.get_by_id(sender_id)
    if not sender:
        return {'status': 'error', 'message': 'User not found'}
    
    # Prepare the message data
    message_data = {
        'sender_id': str(sender.id),
        'sender_name': f"{sender.first_name} {sender.last_name}",
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Send to a room
    if room:
        sio.emit('message', message_data, room=room)
        logger.info(f"Message sent to room {room}: {message}")
        return {'status': 'sent', 'to': f'room:{room}'}
    
    # Send to a specific user
    elif recipient_id:
        if recipient_id in connected_users:
            recipient_sid = connected_users[recipient_id]
            sio.emit('private_message', message_data, room=recipient_sid)
            logger.info(f"Private message sent to user {recipient_id}")
            return {'status': 'sent', 'to': f'user:{recipient_id}'}
        else:
            return {'status': 'error', 'message': 'Recipient not connected'}
    
    # No target specified
    else:
        return {'status': 'error', 'message': 'No recipient or room specified'}

@sio.event
def disconnect(sid):
    """Handle socket disconnection."""
    logger.info(f"Client disconnected: {sid}")
    
    # Remove the disconnected user from connected_users
    for user_id, socket_id in list(connected_users.items()):
        if socket_id == sid:
            del connected_users[user_id]
            logger.info(f"Removed user {user_id} from connected users")
            break

# Helper functions
def notify_user(user_id, event, data):
    """Send a notification to a specific user."""
    if user_id in connected_users:
        sio.emit(event, data, room=connected_users[user_id])
        return True
    return False

def notify_room(room, event, data):
    """Send a notification to all users in a room."""
    sio.emit(event, data, room=room)
    return True

def get_online_users():
    """Get a list of currently connected user IDs."""
    return list(connected_users.keys())

# Example custom events
@sio.event
def user_typing(sid, data):
    """Broadcast when a user is typing."""
    if 'room' in data:
        sio.emit('user_typing', {
            'user_id': data.get('user_id'),
            'is_typing': data.get('is_typing', True)
        }, room=data['room'], skip_sid=sid)  # Skip the sender
        return {'status': 'broadcasted'}
    return {'status': 'error', 'message': 'Room is required'}

@sio.event
def user_online_status(sid, data):
    """Update and broadcast user's online status."""
    if 'user_id' not in data or 'is_online' not in data:
        return {'status': 'error', 'message': 'User ID and status are required'}
    
    user_id = data['user_id']
    is_online = data['is_online']
    
    # Update the user's online status in the database
    mongo.db.users.update_one(
        {'_id': user_id},
        {'$set': {'is_online': is_online, 'last_seen': datetime.utcnow()}}
    )
    
    # Broadcast the status update to relevant users (e.g., friends, chat participants)
    # This is a simplified example - you would need to implement the actual logic
    # for determining who should be notified
    
    return {'status': 'updated', 'user_id': user_id, 'is_online': is_online}
