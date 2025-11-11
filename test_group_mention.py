"""
Test script for group mention detection logic.
"""

class MockMentionee:
    def __init__(self, user_id):
        self.user_id = user_id

class MockMention:
    def __init__(self, mentionees):
        self.mentionees = mentionees

class MockMessage:
    def __init__(self, text, mention=None):
        self.text = text
        self.mention = mention
        self.type = "text"

class MockSource:
    def __init__(self, source_type, user_id=None, group_id=None, room_id=None):
        self.type = source_type
        self.user_id = user_id
        self.group_id = group_id
        self.room_id = room_id

class MockEvent:
    def __init__(self, source, message):
        self.source = source
        self.message = message

def is_bot_mentioned(event, bot_user_id: str) -> bool:
    """
    Check if the bot is mentioned in a group/room message.
    Returns True for 1-on-1 chat, or if bot is mentioned in group/room.

    Args:
        event: MessageEvent from LINE webhook
        bot_user_id: Bot's user ID
    """
    # In 1-on-1 chat, always respond
    if event.source.type == "user":
        return True

    # In group/room, check if bot is mentioned
    if hasattr(event.message, 'mention') and event.message.mention:
        mentionees = event.message.mention.mentionees
        for mentionee in mentionees:
            # Check if this mention is for the bot by comparing user_id
            if hasattr(mentionee, 'user_id') and mentionee.user_id == bot_user_id:
                return True

    return False

def get_reply_target(event) -> str:
    """
    Get the correct reply target ID based on the message source.
    Returns group_id for group chat, user_id for 1-on-1 chat.
    """
    if event.source.type == "group":
        return event.source.group_id
    elif event.source.type == "room":
        return event.source.room_id
    else:
        return event.source.user_id

# Test cases
print("Testing mention detection logic...\n")

# Define test user IDs
BOT_USER_ID = "Ua4be5618a393402d5b7502c7a311478b"  # Bot's user ID
OTHER_USER_ID = "U7181eb0127f4c0922a7333353a1d8118"  # Other user's ID

# Test 1: 1-on-1 chat (should always respond)
print("Test 1: 1-on-1 chat")
event1 = MockEvent(
    source=MockSource("user", user_id="U123456"),
    message=MockMessage("Hello bot")
)
result1 = is_bot_mentioned(event1, BOT_USER_ID)
print(f"  Result: {result1} (Expected: True)")
print(f"  Reply target: {get_reply_target(event1)} (Expected: U123456)")
assert result1 == True, "Failed: Should respond in 1-on-1 chat"
print("  ✅ PASSED\n")

# Test 2: Group chat without mention (should NOT respond)
print("Test 2: Group chat without mention")
event2 = MockEvent(
    source=MockSource("group", group_id="G123456"),
    message=MockMessage("Just chatting")
)
result2 = is_bot_mentioned(event2, BOT_USER_ID)
print(f"  Result: {result2} (Expected: False)")
assert result2 == False, "Failed: Should not respond without mention"
print("  ✅ PASSED\n")

# Test 3: Group chat with bot mentioned (should respond)
print("Test 3: Group chat with bot mentioned")
event3 = MockEvent(
    source=MockSource("group", group_id="G123456"),
    message=MockMessage(
        "Hey @bot, help me",
        mention=MockMention([MockMentionee(user_id=BOT_USER_ID)])
    )
)
result3 = is_bot_mentioned(event3, BOT_USER_ID)
print(f"  Result: {result3} (Expected: True)")
print(f"  Reply target: {get_reply_target(event3)} (Expected: G123456)")
assert result3 == True, "Failed: Should respond when mentioned"
assert get_reply_target(event3) == "G123456", "Failed: Should reply to group"
print("  ✅ PASSED\n")

# Test 4: Group chat with other user mentioned (should NOT respond)
print("Test 4: Group chat with other user mentioned")
event4 = MockEvent(
    source=MockSource("group", group_id="G123456"),
    message=MockMessage(
        "Hey @someone",
        mention=MockMention([MockMentionee(user_id=OTHER_USER_ID)])
    )
)
result4 = is_bot_mentioned(event4, BOT_USER_ID)
print(f"  Result: {result4} (Expected: False)")
assert result4 == False, "Failed: Should not respond when other user mentioned"
print("  ✅ PASSED\n")

# Test 5: Room chat with bot mentioned
print("Test 5: Room chat with bot mentioned")
event5 = MockEvent(
    source=MockSource("room", room_id="R123456"),
    message=MockMessage(
        "@bot help",
        mention=MockMention([MockMentionee(user_id=BOT_USER_ID)])
    )
)
result5 = is_bot_mentioned(event5, BOT_USER_ID)
print(f"  Result: {result5} (Expected: True)")
print(f"  Reply target: {get_reply_target(event5)} (Expected: R123456)")
assert result5 == True, "Failed: Should respond when mentioned in room"
assert get_reply_target(event5) == "R123456", "Failed: Should reply to room"
print("  ✅ PASSED\n")

print("=" * 50)
print("All tests passed! ✅")
print("=" * 50)
