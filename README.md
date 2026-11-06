# contracts

Контракты событий Kafka между микросервисами QuantumVPN — единственный источник правды о том, как сервисы общаются.

| Событие | Топик | Кто пишет | Кто читает |
|---|---|---|---|
| `TrialActivated` | `user.trial-activated` | tg-user-service | tg-subscription-service |
| `PaymentSucceeded` | `payment.succeeded` | tg-payment-service | tg-subscription-service |
| `ExtendAccessRequested` | `provisioning.extend-requested` | tg-subscription-service | tg-provisioning-service |
| `AccessExtended` | `provisioning.access-extended` | tg-provisioning-service | tg-subscription-service |
| `ProvisioningFailed` | `provisioning.failed` | tg-provisioning-service | tg-subscription-service, tg-notification-service |
| `SubscriptionExtended` | `subscription.extended` | tg-subscription-service | tg-notification-service, tg-user-service |

Ключ сообщения — `tg_id`: события одного пользователя лежат в одной партиции и обрабатываются по порядку.

## Совместимость

- [`schemas/`](schemas) — JSON Schema каждого события, [`asyncapi.yaml`](asyncapi.yaml) — описание всех каналов (AsyncAPI 3.0).
- CI падает, если изменение ломает старых потребителей: удалили поле, сменили тип, сделали новое поле обязательным.
  Добавлять можно только необязательные поля. Ломающее изменение = новое событие (`…V2`) и мажорная версия пакета.

```bash
python -m quantum_contracts.schema export   # после изменения событий — обновить schemas/ и asyncapi.yaml
python -m quantum_contracts.schema check    # проверка совместимости (запускается в CI)
```

## Подключение

```toml
dependencies = ["quantum-contracts @ git+https://github.com/ResistVPNservice/contracts.git@v1.0.0"]
```
