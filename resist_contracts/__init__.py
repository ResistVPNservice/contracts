"""Контракты событий ResistVPN: единственный источник правды о том, как сервисы общаются через Kafka."""

from resist_contracts.events import (
    ALL_EVENTS,
    AccessExtended,
    Event,
    ExtendAccessRequested,
    GrantSource,
    PaymentSucceeded,
    ProvisioningFailed,
    SubscriptionExtended,
    TrialActivated,
    utcnow,
)

__all__ = [
    "ALL_EVENTS",
    "AccessExtended",
    "Event",
    "ExtendAccessRequested",
    "GrantSource",
    "PaymentSucceeded",
    "ProvisioningFailed",
    "SubscriptionExtended",
    "TrialActivated",
    "utcnow",
]
