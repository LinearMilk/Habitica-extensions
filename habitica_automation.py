import requests
import datetime
import logging
import json
import re

def main():
    users = load_users('users.json')

    for user in users:
        USER_ID = user['user_id']
        API_TOKEN = user['api_token']
        USERNAME = user.get('username', 'UnknownUser')
        criteria = user.get('criteria', {})

        # Get user-specific logger
        logger = get_user_logger(USERNAME)
        logger.info(f"Processing tasks for {USERNAME}")

        headers = {
            'x-client': f'{USER_ID}-ConvertDailiesToTodos',
            'x-api-user': USER_ID,
            'x-api-key': API_TOKEN,
            'Content-Type': 'application/json'
        }

        try:
            # Check if user logged in today
            if not has_logged_in_today(headers, logger):
                logger.info(f"Skipping {USERNAME}, user has not logged in today.")
                continue

            tasks_to_convert = get_dailies_to_convert(headers, criteria, logger)
            for processed_task in tasks_to_convert:
                create_todo_from_daily(processed_task, headers, logger)
                # Mark the Daily as completed
                mark_daily_completed(processed_task['task']['id'], headers, logger)
        except Exception as e:
            logger.error(f'An error occurred for {USERNAME}: {e}')

def load_users(config_path):
    with open(config_path, 'r') as file:
        users = json.load(file)
    return users

def get_user_logger(username):
    logger = logging.getLogger(username)
    logger.setLevel(logging.INFO)

    # Remove previous handlers to prevent duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create file handler
    fh = logging.FileHandler(f'habitica_automation_{username}.log')
    fh.setLevel(logging.INFO)

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
    fh.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(fh)

    return logger

def has_logged_in_today(headers, logger):
    url = 'https://habitica.com/api/v3/user'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error("Failed to fetch user data.")
        return False

    user_data = response.json().get('data', {})
    auth = user_data.get('auth', {})
    timestamps = auth.get('timestamps', {})
    updated_timestamp = timestamps.get('updated')
    if not updated_timestamp:
        logger.warning("No updated timestamp found in user data.")
        return False

    last_login_date = datetime.datetime.fromisoformat(updated_timestamp).date()
    today_date = datetime.datetime.now(datetime.UTC).date()

    return last_login_date == today_date

def get_dailies_to_convert(headers, criteria, logger):
    url = 'https://habitica.com/api/v3/tasks/user?type=dailys'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    tasks = response.json()['data']
    tasks_to_convert = []
    for task in tasks:
        processed_task = process_task(task, criteria)
        if processed_task:
            tasks_to_convert.append(processed_task)
    logger.info(f'Found {len(tasks_to_convert)} Dailies to convert.')
    return tasks_to_convert

def process_task(task, criteria):
    # Check if the task is due today
    if not task['isDue']:
        return None

    # Check if the task is already completed
    if task.get('completed'):
        return None

    # Get the notes field
    notes = task.get('notes', '')

    # Get the notes prefix to look for (default is 'Recurrent')
    notes_prefix = criteria.get('notes_prefix', 'Recurrent')

    # Make both notes and notes_prefix lowercase for case-insensitive comparison
    notes_lower = notes.lower()
    notes_prefix_lower = notes_prefix.lower()

    # Check if notes start with the specified prefix (case-insensitive)
    if not notes_lower.startswith(notes_prefix_lower):
        return None

    # Remove the prefix from the original notes (using the length of the original prefix)
    remaining_notes = notes[len(notes_prefix):].lstrip()

    # Use a regular expression to extract the difficulty descriptor (case-insensitive)
    match = re.match(r'(\w+)([\s\S]*)', remaining_notes, re.IGNORECASE)
    if match:
        difficulty_descriptor = match.group(1)
        adjusted_notes = match.group(2).lstrip()
    else:
        # If no difficulty descriptor is found, default to 'Easy'
        difficulty_descriptor = 'Easy'
        adjusted_notes = remaining_notes

    # Map the difficulty descriptor to priority (case-insensitive)
    difficulty_mapping = {
        'Trivial': 0.1,
        'Easy': 1,
        'Medium': 1.5,
        'Hard': 2
    }
    # Capitalize the descriptor to match keys in the mapping
    difficulty_descriptor_cap = difficulty_descriptor.capitalize()
    priority = difficulty_mapping.get(difficulty_descriptor_cap, 1)  # Default to Easy (priority 1)

    # Now, create and return the processed task data
    return {
        'task': task,
        'priority': priority,
        'adjusted_notes': adjusted_notes
    }

def create_todo_from_daily(processed_task, headers, logger):
    daily_task = processed_task['task']
    priority = processed_task['priority']
    adjusted_notes = processed_task['adjusted_notes']

    # Get the checklist from the Daily
    checklist = daily_task.get('checklist', [])

    # Remove 'id' and reset 'completed' fields from checklist items
    # Since these will be new checklist items for the new To-Do
    new_checklist = []
    for item in checklist:
        new_item = {
            'text': item['text'],
            'completed': False  # Reset completed status
        }
        new_checklist.append(new_item)

    url = 'https://habitica.com/api/v3/tasks/user'
    data = {
        'text': daily_task['text'],
        'type': 'todo',
        'notes': adjusted_notes,
        'tags': daily_task.get('tags', []),
        'priority': priority,
        'attribute': daily_task.get('attribute', 'str'),
        'date': (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
        'checklist': new_checklist  # Include the checklist
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        logger.info(f"Created To-Do: {daily_task['text']} with priority {priority}")
    else:
        logger.error(f"Failed to create To-Do: {response.json()}")

def mark_daily_completed(task_id, headers, logger):
    url = f'https://habitica.com/api/v3/tasks/{task_id}/score/up'
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        logger.info(f'Marked Daily as completed: {task_id}')
    else:
        logger.error(f'Failed to mark Daily as completed: {response.json()}')

if __name__ == '__main__':
    main()
