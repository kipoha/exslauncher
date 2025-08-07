from src.utils.notify_system import send_notification

send_notification(
    "Kipoha",
    "Hello world",
    app_name="Kipoha",
    urgency="low",
    color_icon="#a1b2c3",
    # icon="/home/kipoha/.config/fabric_launcher/test.png",
)
