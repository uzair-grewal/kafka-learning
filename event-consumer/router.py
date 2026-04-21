def handle_routing(event):
    """
    Decides where the event should go based on the 'event_type'.
    """
    event_type = event.get('action_type')
    student_id = event.get('student_id')

    print(f"Routing event for Student ID: {student_id}, Event Type: {event_type}")

    # Routing Table
    topic_mapping = {
        'INSERT': 'student_registrations',
        'UPDATE': 'student_profile_changes',
    }

    destination = topic_mapping.get(event_type)

    if destination:
        print(f"Routing {event_type} (ID: {student_id}) -> {destination}")
        return destination
    else:
        print(f"No route found for event type: {event_type}")