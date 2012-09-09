import sys
from eden.msg import search_subscription_notifications

if sys.argv:
    search_subscription_notifications(sys.argv[1])
