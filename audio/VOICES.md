# VOICES — зафиксированные голоса (ElevenLabs через InfarModel)

Модель: `eleven_multilingual_v2` (единственная, как требует RULES.md). Настройки по умолчанию прокси
(stability/similarity/style прокси не принимает — передаются значения по умолчанию модели).

| Герой | voice_id | Имя в библиотеке | Почему |
|---|---|---|---|
| Она | `GN4wbsbejSnGSa1AzjH5` | Ekaterina | женский, естественное московское произношение, без акцента |
| Он | `pvY1pikBdoI4SB62vEVo` | Andrei | мужской, спокойный и дружелюбный, без акцента |

Пробы других женских голосов: `audio/voice_tests/` (Anna, Jessica, Lily — заметный акцент/не тот тембр).

Использованные дубли: везде `_v1`, кроме второго смеха под навесом (`08_she_laugh_s2_v2`, `10_he_laugh_v2`).
Липсинк: Rhubarb 1.13 phonetic (`audio/lipsync/*.json`) — endpoint `with-timestamps` прокси не поддерживает.
