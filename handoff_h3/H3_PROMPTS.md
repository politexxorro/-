# MiniMax H3 — полный пакет: «КАЖДЫЙ ДЕНЬ — С ТОБОЙ»

Это самодостаточное задание. В папке рядом:
- `start_frames/clip01.png … clip21.png` — стартовый кадр для каждого клипа (наши герои уже в нужной позе, ракурсе и свете);
- `references/` — 4 эталонных листа героев (она: эмоции + полный рост, БЕЗ родинки; он: эмоции в худи + полный рост).

## НАСТРОЙКИ H3 (одинаковые для всех клипов)
- Модель: MiniMax H3 (не Lite/Highspeed — они хуже держат героев; Max — можно).
- Режим: Image-to-Video. Start frame = `clipNN.png` этого клипа.
- В референсы (reference images) каждого запроса добавляй все 4 листа из `references/`.
- Разрешение: 1080p (или 2K, если бюджет позволяет). Формат 16:9. Частота — родные 24 fps.
- Длительность: указана у каждого клипа. Если минимум модели 5 с, а клип короче — генерируй 5 с и обрежь при склейке.
- Родной звук H3 ВЫКЛЮЧИ или игнорируй: финальная дорожка — из нашего ролика `final_720p.mp4`.

## ПОРЯДОК РАБОТЫ
1. Генерируй клипы по одному, по промтам ниже (каждый промт полный — копируй целиком).
2. После каждого клипа проверь: герои совпадают с эталонами; пальцы нормальные; движение непрерывное, без телепортов; одежда/причёска не изменились. Провал — перегенерация (обычно 2–3 попытки на клип).
3. Склей клипы встык по порядку 01→21 с длительностями из таблицы (суммарно ровно 120.000 с).
4. Положи звук из `final_720p.mp4` (он уже сведён: голоса, шумы), поверх — русские субтитры:
   0:11.1 Она «Доброе утро, соня!» · 0:23.1 Он «Это… так и задумано было.» · 1:21.6 Он «Для тебя.» ·
   1:33.1 Он «Знаешь… я бы хотел, чтобы каждый день был как сегодня.» · 1:38.1 Она «Глупый… так и будет.» ·
   1:55.0 Она (шёпот) «Мой самый счастливый день… и завтра будет ещё один.»
5. В клипе 21 поверх кадра добавь рукописную надпись «Каждый день — с тобой» (появляется с 1:57, мягкое затемнение к 2:00) — средствами монтажа, НЕ проси модель рисовать текст.
6. Итог: один MP4, H.264, 1920×1080, 24 fps, ровно 120.000 с, звук AAC.

## ТАБЛИЦА КЛИПОВ
| Клип | Таймкод | Длит. | Сцена |
|---|---|---|---|
| 01 | 0:00–0:04 | 4 с (ген. 5, обрезать) | Утро: комната |
| 02 | 0:04–0:08 | 4 с (ген. 5, обрезать) | Утро: тык в щёку |
| 03 | 0:08–0:14 | 6 с | Утро: пробуждение + реплика |
| 04 | 0:14–0:19 | 5 с | Кухня: тесто |
| 05 | 0:19–0:24 | 5 с | Кухня: блин → потолок |
| 06 | 0:24–0:30 | 6 с | Кухня: смех + реплика |
| 07 | 0:30–0:36 | 6 с | Улица: к фотобудке |
| 08 | 0:36–0:44 | 8 с | Фотобудка: 4 вспышки |
| 09 | 0:44–0:48 | 4 с (ген. 5, обрезать) | Фотополоска |
| 10 | 0:48–0:54 | 6 с | Дождь: бег |
| 11 | 0:54–1:00 | 6 с | Дождь: худи-крыша |
| 12 | 1:00–1:08 | 8 с | Навес: лбы |
| 13 | 1:08–1:14 | 6 с | Автомат: прицел |
| 14 | 1:14–1:20 | 6 с | Автомат: 2 промаха + успех |
| 15 | 1:20–1:24 | 4 с (ген. 5, обрезать) | Вручение котика |
| 16 | 1:24–1:30 | 6 с | Закат: общий план |
| 17 | 1:30–1:38 | 8 с | Закат: диалог |
| 18 | 1:38–1:42 | 4 с (ген. 5, обрезать) | Закат: поцелуй-силуэт |
| 19 | 1:42–1:50 | 8 с | Вечер: плед |
| 20 | 1:50–1:56 | 6 с | Вечер: нежный взгляд |
| 21 | 1:56–2:00 | 4 с (ген. 5, обрезать) | Финал: отъезд камеры |

Во всех промтах: GIRL = cute anime girl, 170 cm, very long dark-chestnut hair falling below her waist with middle-parted curtain bangs, big dark-brown eyes with two highlights, no mole, unzipped light-gray oversized hoodie over a black t-shirt, thin silver necklace, black wide track pants with two white side stripes gathered at the ankles, chunky white sneakers. BOY = soft chubby anime boy, 181 cm, round face, fluffy dark hair, small narrow dark-brown eyes, gentle shy smile, light-gray hoodie with plaid-lined hood, black t-shirt, light-blue baggy jeans, white-gray sneakers, no glasses, no necklace.

STYLE (хвост каждого промта): clean 2D anime cel shading with soft two-tone shadows, thin dark outlines (thinner on faces), warm cinematic color grade, soft bloom, smooth continuous motion with gentle ease-in/ease-out, subtle breathing and occasional blinks, characters must exactly match the attached reference sheets in every frame. Negative: 3D render, photorealism, extra fingers, deformed hands, second mouth, changing hairstyle or outfit, mole on the girl's face, glasses, melting or morphing artifacts, jittering outlines, any text or watermark.

---

## ПРОМТЫ (копируй целиком, один промт = один клип)

### CLIP 01 — 0:00–0:04 (ген. 5 с)
Cozy anime bedroom in the early morning, warm golden sunlight streaming from a window at back-right, peach-colored soft shadows, dust motes floating and sparkling in the light beams. A BOY (soft chubby anime boy, 181 cm, round face, fluffy dark hair) is asleep in bed fully covered by a blanket; the blanket rises and falls slowly with his breathing. Camera: slow gentle push-in from a wide shot toward the bed. No people moving except the breathing blanket; curtains sway almost imperceptibly. Clean 2D anime cel shading with soft two-tone shadows, thin dark outlines, warm cinematic color grade, soft bloom, smooth continuous motion. Negative: 3D render, photorealism, extra fingers, morphing artifacts, jittering outlines, any text or watermark.

### CLIP 02 — 0:04–0:08 (ген. 5 с)
Anime bedroom, morning, warm golden light from back-right, peach shadows. Bed-level camera: a GIRL (cute anime girl, 170 cm, very long dark-chestnut hair below her waist, curtain bangs, big dark-brown eyes, no mole, unzipped light-gray oversized hoodie over black t-shirt, thin silver necklace, black track pants with two white side stripes, chunky white sneakers) tiptoes into frame with a sly playful smile, leans in slowly, stretches out one finger and gently pokes the sleeping BOY (chubby, round face, fluffy dark hair, under a blanket) on the cheek. Her hair sways softly as she moves. Camera static with a tiny slow drift. Clean 2D anime cel shading, thin dark outlines, warm cinematic grade, soft bloom, smooth continuous motion, subtle breathing, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, deformed hands, mole on the girl's face, changing outfit, morphing artifacts, any text or watermark.

### CLIP 03 — 0:08–0:14 (6 с)
Anime bedroom, morning, warm golden light. Close-up of the BOY (soft chubby anime boy, round face, fluffy dark hair, small narrow dark-brown eyes): his eyes snap open in comic surprise, hair bounces, brief startled shake — then cut-like reframe to the GIRL's face (cute anime girl, long dark-chestnut hair, big dark-brown eyes, no mole, light-gray hoodie): she laughs warmly and speaks a short cheerful line (mouth moves naturally for about 1.5 seconds, Russian speech «Доброе утро, соня!»), then the boy smiles sleepily, embarrassed, and pulls a pillow over his head. Camera: intimate close-ups, gentle handheld-like micro movement. Clean 2D anime cel shading, thin dark outlines, warm cinematic grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, second mouth, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 04 — 0:14–0:19 (5 с)
Cozy anime kitchen, warm creamy daylight from a window on the left, soft shadows. The BOY (soft chubby anime boy, round face, fluffy dark hair, light-gray hoodie with plaid-lined hood, black t-shirt, light-blue baggy jeans, wearing an apron, a dab of flour on his nose) energetically whisks pancake batter in a bowl, rhythmic circular motion, concentrated cute expression. The GIRL (long dark-chestnut hair below waist, no mole, light-gray oversized hoodie, black track pants with white stripes) leans on the counter beside him, chin on her hand, watching him with an affectionate amused smile, occasionally blinking. Light steam/flour puffs. Camera: static medium shot, slight slow push-in. Clean 2D anime cel shading, thin dark outlines, warm cinematic grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, deformed hands, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 05 — 0:19–0:24 (5 с)
Anime kitchen, warm creamy light. The BOY (chubby anime boy in apron over light-gray hoodie, flour on nose) dramatically flips a pancake from the frying pan with a confident flourish — the pancake flies up out of frame; he looks up proudly; beat of silence; the pancake stays STUCK TO THE CEILING; then it peels off and plops down flat onto his head. His expression goes from proud to deadpan. The GIRL (long dark-chestnut hair, no mole, gray oversized hoodie) watches and starts to crack up. Camera: medium shot, slight tilt up following the pancake then back down. Comic timing, smooth continuous motion. Clean 2D anime cel shading, thin dark outlines, warm cinematic grade, soft bloom, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, deformed face, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 06 — 0:24–0:30 (6 с)
Anime kitchen, warm creamy light. The GIRL (long dark-chestnut hair below waist, big brown eyes, no mole, light-gray oversized hoodie) is laughing so hard she wipes a tear, holding her stomach, shoulders shaking. The BOY (chubby, round face, pancake draped on his fluffy dark hair) stands with dignity, raises one finger and delivers a deadpan line (mouth moves naturally for about 2 seconds, Russian speech «Это… так и задумано было.»), small proud nod, pancake slides slightly. Camera: two-shot, static with subtle breathing movement. Clean 2D anime cel shading, thin dark outlines, warm cinematic grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, second mouth, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 07 — 0:30–0:36 (6 с)
Anime city street in the daytime, neutral soft daylight from upper right, light lilac shadows, cozy storefronts. The GIRL and the BOY (she: very long dark-chestnut hair, no mole, light-gray oversized hoodie, black track pants with white stripes, chunky white sneakers; he: chubby, fluffy dark hair, light-gray hoodie, light-blue baggy jeans) walk hand in hand toward the camera, relaxed happy stroll; she suddenly notices a photo booth off-screen, her eyes light up with sparkles, she points excitedly and tugs him by the hand, pulling him along; he stumbles one step and smiles shyly. Her long hair and hoodie sway with the motion. Camera: tracking shot, smooth lateral follow. Clean 2D anime cel shading, thin dark outlines, warm cinematic grade, soft bloom, smooth continuous walking animation, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, deformed legs, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 08 — 0:36–0:44 (8 с)
Inside a cramped anime photo booth, curtain behind, even flat lighting punctuated by bright camera flashes. The GIRL (long dark-chestnut hair, no mole, light-gray hoodie) and the BOY (chubby, fluffy dark hair, light-gray hoodie) squeezed together on the bench, four photo flashes in sequence, one pose per flash with quick fun transitions between: (1) both make silly faces sticking out tongues; (2) they form a heart together with their hands; (3) he is flustered and embarrassed while she laughs pointing at him; (4) she kisses his cheek and he blushes bright red with wide eyes. Each flash briefly whites out the frame. Camera: static front view like the booth camera. Playful comic energy, smooth transitions between poses. Clean 2D anime cel shading, thin dark outlines, warm cinematic grade, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, deformed hands, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 09 — 0:44–0:48 (ген. 5 с)
Anime street next to a photo booth, soft daylight. Close two-shot from slightly above: the GIRL (long dark-chestnut hair, no mole, gray hoodie) and the BOY (chubby, fluffy dark hair, gray hoodie) lean their heads together over a fresh photo strip with four little pictures, holding it between them; both smile warmly, she giggles and points at one photo, he nods with a soft embarrassed smile. Gentle breeze moves her hair strands. Camera: slow subtle push-in on the strip and their faces. Tender quiet mood. Clean 2D anime cel shading, thin dark outlines, warm cinematic grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, readable text on the photo strip, mole on the girl's face, morphing artifacts, any watermark.

### CLIP 10 — 0:48–0:54 (6 с)
Anime street in sudden heavy rain, cold diffused light, blue-violet shadows, wet asphalt with reflections, rain streaks on 1s. The GIRL and the BOY (she: long dark-chestnut hair getting wet, no mole, light-gray hoodie; he: chubby, fluffy dark hair, light-gray hoodie, baggy jeans) run together through the rain laughing, splashes under their sneakers, she holds her hood half-up, both soaked and happy. Camera: dynamic lateral tracking shot following the run, slight motion blur on the background. Energetic joyful motion, natural run cycle. Clean 2D anime cel shading, thin dark outlines, cool cinematic grade with warm faces, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, broken run cycle, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 11 — 0:54–1:00 (6 с)
Anime street in heavy rain, cold blue-violet light, wet reflections. Mid-run: the BOY (chubby, fluffy dark hair, black t-shirt now visible) pulls off his light-gray hoodie and stretches it over both their heads like a roof; the GIRL (long wet dark-chestnut hair, no mole, gray oversized hoodie) ducks under it close to him, laughing; they keep running together side by side under the hoodie-roof, rain streaming off its edges, synchronized steps, splashes. Camera: frontal tracking shot, both in frame. Warm intimacy inside cold rain. Clean 2D anime cel shading, thin dark outlines, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, hoodie changing color, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 12 — 1:00–1:08 (8 с)
Under a small awning at night-dark rainy street, rain falling beyond the edge, cold blue light, soft reflections. The GIRL (soaked long dark-chestnut hair, darker when wet, no mole, gray hoodie) and the BOY (chubby, wet fluffy hair, black t-shirt, holding his wet hoodie) stand close face to face, breathing hard from running, laughing — the laughter slowly fades into a tender look; they lean in and gently touch foreheads, eyes closing, small smiles, drops falling from their hair. No dialogue. Camera: very slow push-in from medium to close-up. Quiet intimate emotional peak. Clean 2D anime cel shading, thin dark outlines, cool grade with warm skin tones, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, kissing on lips, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 13 — 1:08–1:14 (6 с)
Anime arcade interior at night, pink-purple neon glow from the left, colorful machine lights bokeh in background. The BOY (chubby, round face, fluffy dark hair, light-gray hoodie) stands at a claw machine, hands on the joystick, tongue slightly out in deep concentration, neon reflections on his face; the GIRL (long dark-chestnut hair, no mole, gray oversized hoodie) stands beside him cheering, fists clenched with excitement, bouncing slightly on her toes, eyes sparkling. Inside the glass: a cute plush cat among toys. Camera: medium two-shot, slight slow push-in toward the glass. Clean 2D anime cel shading, thin dark outlines, neon cinematic grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, readable text on machines, mole on the girl's face, morphing artifacts, any watermark.

### CLIP 14 — 1:14–1:20 (6 с)
Anime arcade, pink-purple neon. Through the claw machine glass: the metal claw grabs a plush cat, lifts it — the cat slips and drops (the GIRL outside slumps in comic despair); second try — drops again (she covers her eyes peeking through fingers); third try — the claw holds, carries the plush cat and drops it into the prize chute, success! The BOY pumps his fist, the GIRL jumps with joy, hands clasped. Camera: alternating view through glass and reaction shots feel, continuous smooth motion, comic timing with a triumphant beat. Clean 2D anime cel shading, thin dark outlines, neon grade, characters must exactly match the attached reference sheets (she: no mole, long dark-chestnut hair, gray hoodie; he: chubby, fluffy dark hair, gray hoodie). Negative: 3D render, photorealism, extra fingers, claw morphing, readable text, mole on the girl's face, any watermark.

### CLIP 15 — 1:20–1:24 (ген. 5 с)
Anime arcade, pink-purple neon glow. Close two-shot: the BOY (chubby, round face, fluffy dark hair, light-gray hoodie) proudly holds out a plush cat with both hands to the GIRL and says a short line (mouth moves naturally for about 1 second, Russian speech «Для тебя.»), shy proud smile, slight blush. The GIRL (long dark-chestnut hair, big brown eyes, no mole, gray oversized hoodie) gasps softly, takes the plush cat and hugs it tight against her chest, beaming with happiness, eyes sparkling, swaying a little with joy. Camera: static intimate close-up, neon rim light. Clean 2D anime cel shading, thin dark outlines, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, second mouth, mole on the girl's face, plush cat changing shape, morphing artifacts, any text or watermark.

### CLIP 16 — 1:24–1:30 (6 с)
Anime hilltop/embankment at golden sunset, sun low at back-right, golden rim light, pink-lilac sky with soft clouds, gentle wind. Wide shot from behind: the GIRL (very long dark-chestnut hair flowing in the wind, gray oversized hoodie, plush cat on her lap) and the BOY (chubby, fluffy dark hair, light-gray hoodie) sit side by side on the grass/bench silhouetted against the sunset; she slowly leans over and rests her head on his shoulder; his head tilts gently toward hers. Hair and grass sway in the wind, lens flare glints. Camera: static wide, very slow drift. Calm romantic mood. Clean 2D anime cel shading, warm golden grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra limbs, silhouettes merging, morphing artifacts, any text or watermark.

### CLIP 17 — 1:30–1:38 (8 с)
Golden sunset, warm backlight, pink-lilac sky, wind in hair. Alternating intimate close-ups: the BOY (chubby, round face, fluffy dark hair backlit gold, light-gray hoodie) gazes at the horizon, then turns to her and speaks softly (mouth moves naturally for about 3 seconds, Russian speech «Знаешь… я бы хотел, чтобы каждый день был как сегодня.»); then the GIRL (long dark-chestnut hair glowing in backlight, big brown eyes glistening with warm tears of happiness, no mole) answers with a tender smile (mouth moves for about 2 seconds, Russian speech «Глупый… так и будет.»). Hair strands float in the wind, golden particles in the air. Camera: slow gentle push-ins on each face. Clean 2D anime cel shading, warm golden grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, second mouth, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 18 — 1:38–1:42 (ген. 5 с)
Golden sunset, sun disc low on the horizon, pink-lilac sky. Silhouette two-shot against the sun: the GIRL (long flowing hair silhouette) and the BOY (soft round silhouette) lean toward each other slowly and share one gentle tender kiss, rim-lit edges glowing gold, lens flare blooming softly at the moment of the kiss, wind moving her long hair. Camera: static silhouette composition, slow subtle zoom. Extremely tender, tasteful, romantic. Clean 2D anime cel shading, warm golden grade, strong soft bloom, smooth continuous motion. Negative: 3D render, photorealism, extra limbs, silhouettes deforming or merging, morphing artifacts, any text or watermark.

### CLIP 19 — 1:42–1:50 (8 с)
Cozy anime living room at night: amber floor lamp on the left, bluish TV screen flicker from the front, warm string lights in background, soft shadows. The BOY (chubby, round face, fluffy dark hair, light-gray hoodie) has fallen asleep sitting on the sofa, head tilted, breathing slowly. The GIRL (long dark-chestnut hair, no mole, gray oversized hoodie) quietly picks up a soft blanket and gently drapes it over him, careful slow movements, tucking the edge; on the coffee table nearby: the plush cat and the photo strip from the booth. Camera: slow lateral drift, warm intimate framing. Clean 2D anime cel shading, thin dark outlines, warm amber grade with cool screen flicker, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, blanket morphing, mole on the girl's face, readable text, any watermark.

### CLIP 20 — 1:50–1:56 (6 с)
Cozy anime living room at night, amber lamp light, soft screen flicker, string lights bokeh. The GIRL (long dark-chestnut hair, big warm brown eyes, no mole, gray oversized hoodie) sits down softly on the sofa next to the sleeping BOY (chubby, fluffy dark hair, under a blanket, breathing slowly), looks at him with deep tenderness, a small loving smile; she whispers almost inaudibly (very subtle mouth movement around second 5, Russian whisper «Мой самый счастливый день…»), then rests her head carefully against his shoulder, eyes soft. Camera: slow push-in on her face then settling. Quiet warm emotional glow. Clean 2D anime cel shading, warm amber grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra fingers, second mouth, mole on the girl's face, morphing artifacts, any text or watermark.

### CLIP 21 — 1:56–2:00 (ген. 5 с)
Cozy anime living room at night, amber lamp, string lights, TV flicker. Wide shot: the GIRL (long dark-chestnut hair, no mole, gray hoodie) nestled against the sleeping BOY (chubby, under blanket) on the sofa, both peaceful; plush cat and photo strip on the coffee table in foreground. Camera: slow smooth pull-back away from the couple, widening the cozy frame, lights twinkling gently, everything calm and warm; gradual gentle darkening toward the end of the clip. No on-screen text (the handwritten title will be added in editing). Clean 2D anime cel shading, warm amber grade, soft bloom, smooth continuous motion, characters must exactly match the attached reference sheets. Negative: 3D render, photorealism, extra limbs, morphing artifacts, any text or watermark.

---

## ЧЕК-ЛИСТ ПРИЁМКИ КАЖДОГО КЛИПА
1. Стоп-кадр в 3 случайных местах: лица и одежда совпадают с эталонами; у неё НЕТ родинки; у него НЕТ очков/цепочки.
2. Руки: 5 пальцев, не плавятся.
3. Движение непрерывно, позы не телепортируются, контуры не дрожат.
4. Одежда и причёска не меняются внутри клипа и между клипами.
5. На репликах рот движется, в паузах закрыт. В кадре нет случайного текста.
Провал любого пункта — перегенерация этого клипа (стартовый кадр и референсы те же, промт можно уточнить).
