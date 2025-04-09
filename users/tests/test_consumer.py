import pytest
import asyncio


@pytest.mark.asyncio
async def test_connection(producer):
    assert producer.is_connected() is True
    

@pytest.mark.asyncio
async def test_declare_exchange(producer):
    from app.producer.conf import USER_RABBITMQ_EXCHANGE

    assert producer.exchange is not None
    assert producer.exchange.name == USER_RABBITMQ_EXCHANGE.name


@pytest.mark.asyncio
async def test_user_creation_message(producer, consumer_received_messages):
    from app.producer.conf import USER_CREATION_RABBITMQ_QUEUE, USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE, USER_PASSWORD_FORGET_RABBITMQ_QUEUE

    test_data = {"user_id": "123", "email": "test@example.com", "name": "Test User"}
    await producer.send_user_creation_message(test_data)
    
    # Wait for message processing
    await asyncio.sleep(1)
    
    # Assert message was delivered to the correct queue
    assert len(consumer_received_messages[USER_CREATION_RABBITMQ_QUEUE.name]) == 1
    assert consumer_received_messages[USER_CREATION_RABBITMQ_QUEUE.name][0] == test_data
    
    # Verify message was not sent to other queues
    assert len(consumer_received_messages[USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name]) == 0
    assert len(consumer_received_messages[USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name]) == 0


@pytest.mark.asyncio
async def test_email_verification_message(producer, consumer_received_messages):
    from app.producer.conf import USER_CREATION_RABBITMQ_QUEUE, USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE, USER_PASSWORD_FORGET_RABBITMQ_QUEUE
    
    test_data = {"user_id": "123", "verification_token": "abc123"}
    await producer.send_user_email_verification_message(test_data)
    
    # Wait for message processing
    await asyncio.sleep(1)
    
    # Assert message was delivered to the correct queue
    assert len(consumer_received_messages[USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name]) == 1
    assert consumer_received_messages[USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name][0] == test_data
    
    # Verify message was not sent to other queues
    assert len(consumer_received_messages[USER_CREATION_RABBITMQ_QUEUE.name]) == 0
    assert len(consumer_received_messages[USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name]) == 0


@pytest.mark.asyncio
async def test_password_forget_message(producer, consumer_received_messages):
    from app.producer.conf import USER_CREATION_RABBITMQ_QUEUE, USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE, USER_PASSWORD_FORGET_RABBITMQ_QUEUE

    test_data = {"user_id": "123", "reset_token": "xyz789"}
    await producer.send_user_password_forget_message(test_data)
    
    # Wait for message processing
    await asyncio.sleep(1)
    
    # Assert message was delivered to the correct queue
    assert len(consumer_received_messages[USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name]) == 1
    assert consumer_received_messages[USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name][0] == test_data
    
    # Verify message was not sent to other queues
    assert len(consumer_received_messages[USER_CREATION_RABBITMQ_QUEUE.name]) == 0
    assert len(consumer_received_messages[USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name]) == 0


@pytest.mark.asyncio
async def test_multiple_messages(producer, consumer_received_messages):
    from app.producer.conf import USER_CREATION_RABBITMQ_QUEUE, USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE, USER_PASSWORD_FORGET_RABBITMQ_QUEUE
  
    # Send messages to all queues
    user_data = {"user_id": "456", "email": "another@example.com"}
    verification_data = {"user_id": "456", "verification_token": "def456"}
    password_data = {"user_id": "456", "reset_token": "ghi789"}
    
    await producer.send_user_creation_message(user_data)
    await producer.send_user_email_verification_message(verification_data)
    await producer.send_user_password_forget_message(password_data)
    
    # Wait for message processing
    await asyncio.sleep(1)
    
    # Verify messages were delivered to correct queues
    assert len(consumer_received_messages[USER_CREATION_RABBITMQ_QUEUE.name]) == 1
    assert consumer_received_messages[USER_CREATION_RABBITMQ_QUEUE.name][0] == user_data
    
    assert len(consumer_received_messages[USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name]) == 1
    assert consumer_received_messages[USER_EMAIL_VERIFICATION_RABBITMQ_QUEUE.name][0] == verification_data
    
    assert len(consumer_received_messages[USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name]) == 1
    assert consumer_received_messages[USER_PASSWORD_FORGET_RABBITMQ_QUEUE.name][0] == password_data
