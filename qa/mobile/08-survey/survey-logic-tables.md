# Survey — таблиці логіки переходів (еталон для тестів)

> **Статус: перевірено на апці (recon 8, 2026-09-24) — усі перевірені рядки збіглися** (MO5-0…5, T8-1…3, END-1, END-3, FIB-2,
> FIB-3, TWO-8, TWO-12, TWO-14). Власнику лишається одне рішення — **TWO-15** (правило «назад» в іншу секцію).
> Ці таблиці — оракул тестів логіки: тест порівнює, які питання **видно** на екрані, з рядком таблиці. У тести не
> переписується рушій логіки — лише очікування звідси.

Джерело: визначення опитувань DEV (`survey-definitions/*.json`, `GET /survey/{id}`, 2026-09-24). Правила висять на
**варіантах відповіді**: `answers[].logic = {when: eq true, actions: [skipToField → targetFieldId]}`. Номери Q тут —
порядок у шаблоні (у самій апці номери показуються лише для видимих питань і зсуваються, тож тести шукають питання
**за текстом**, а в повторюваних секціях — за текстом у межах картки екземпляра).

## Правила читання (як працює і шаблон, і апка — перевір)

1. Поки на питання з правилом не відповіли — **видно все**.
2. «Перейти до Qn» (вперед) ховає питання **строго між** відповіддю і Qn. Qn і все після нього — видно (якщо їх не
   сховає інше правило).
3. «Кінець» (`__end__`) ховає **все після** цього питання в усьому опитуванні; кнопка «Repeat section» зникає.
4. «Далі» (`__next__` / порожньо) — нічого не ховає.
5. Правило «назад» (ціль вище за питання) — **ігнорується** (D-SRV-16).
6. У **повторюваній** секції правило діє лише в **своєму** екземплярі. Правило, що веде **за межі** секції: екземпляр
   закінчується на цьому питанні, опитування продовжується з цілі (між секцією і ціллю — сховано); якщо ціль — у іншій
   повторюваній секції, це її **перший** екземпляр.
7. Сховане питання **не відправляється** (його відповіді немає в збереженому опитуванні).

---

## Short Survey — логіки немає

Питання «Good?» (Yes/No), «Text?». Видно завжди обидва.

## Mo3 All Question Types — логіка без ефекту

Правила лише «Далі» (у «Was the job completed successfully?» Yes / No). Видно завжди всі 7 питань.

## Mo5 Radio Logic Mapping (секція «Issue Routing», 5 питань)

Q1 «What issue type was identified on site?» → Q2 «Q2 Describe the site access issue», Q3 «Q3 Select the missing or
damaged equipment», Q4 «Q4 Select the follow-up visit date», Q5 «Q5 Enter customer-related notes».

| # | Відповідь на Q1 | Правило | Видно | Сховано |
|---|---|---|---|---|
| MO5-0 | (ще немає) | — | Q1–Q5 | — |
| MO5-1 | Access issue | → Q2 | Q1, Q2, Q3, Q4, Q5 | — |
| MO5-2 | Equipment issue | → Q3 | Q1, Q3, Q4, Q5 | Q2 |
| MO5-3 | Customer issue | далі | Q1–Q5 | — |
| MO5-4 | No issue found | → Q4 | Q1, Q4, Q5 | Q2, Q3 |
| MO5-5 | No issue found → **змінити** на Access issue | — | Q1–Q5 (Q2, Q3 повертаються) | — |

> Зауваж: назва каже «кожен варіант — свій шлях», але за правилом 2 «Access issue» не ховає Q3–Q5 (у Q2 немає свого
> переходу). Еталон — правила шаблону, а не назва.

## T8 Branching Workflow (4 секції, 6 питань)

S1 «S1 Job Entry»: Q1 «S1Q3 Was the site ready?» · S2 «S2 Site Ready Path»: Q2 «S2Q5 Which tasks were completed?» ·
S3 «S3 Site Not Ready Path»: Q3 «S3Q6 What blocked the work?», Q4 «S3Q7 Describe the blocker» · S4 «S4 Closure»:
Q5 «S4Q9 Add final summary», Q6 «S4Q8 Upload evidence photo».

| # | Відповідь на Q1 | Правило | Видно | Сховано |
|---|---|---|---|---|
| T8-1 | Yes | далі | усі 6 (усі 4 секції) | — |
| T8-2 | No | → Q3 | Q1, Q3–Q6 | Q2 — **секція S2 зникає** |
| T8-3 | No → **змінити** на Yes | — | усі 6 (S2 повертається) | — |

## End Survey (Q1 окремо + повторювана секція «S1 Job Details…» з Q2–Q15)

Q1 «End Survey» · у секції: Q2 «Q1 Enter the work order ID», Q3 «Q2 text Select the visit date», Q4 «Q3 photo Question»,
Q5 «Q4 Select the technician arrival time», Q6 «Q5 time Question», Q7 «Q6 date Question», Q8 «Q7 yes/no Question»,
Q9 «Q8 Radio Question», Q10 «Q9 test question», Q11 «Q10 photo question», Q12 «Q11 Checkbox Question», Q13 «Bad?»,
Q14 «Good?», Q15 «Problems?».

| # | Відповідь | Правило | Видно | Сховано |
|---|---|---|---|---|
| END-1 | Q1 «End Survey» = Yes | кінець | лише Q1 → **Save активна** | уся секція (Q2–Q15) |
| END-2 | Q1 = No | далі | Q1 + секція | — |
| END-3 | у екземплярі: «Q1 Enter the work order ID» = Yes | кінець | Q1, у екземплярі лише це питання; **«Repeat section» немає** | решта екземпляра (Q3–Q15) |
| END-4 | у екземплярі: «Q4 Select the technician arrival time» = No | → Q7 | усе, крім Q6 | Q6 «Q5 time Question» |
| END-5 | у екземплярі: «Q7 yes/no Question» = No | → Q10 | усе, крім Q9 | Q9 «Q8 Radio Question» |
| END-6 | «Q8 Radio Question» = Option 2 Q8 | → Q11 | усе, крім Q10 | Q10 «Q9 test question» |
| END-7 | «Q8 Radio Question» = Option 3 Q8 | → Q12 | усе, крім Q10, Q11 | Q10, Q11 |
| END-8 | «Q8 Radio Question» = Option 4 Q8 | кінець | до Q9 включно; **«Repeat section» немає** | Q10–Q15 |

## Fiber Site Survey (14 питань; повторювані «Room Information», «Fiber installation report…», «… (Copy)»)

Q1 «Are there any rooms to survey on this site?» (Yes / No) · «Room Information»: Q2 «Room name / number», Q3 «Room type»,
Q4 «Number of outlets» (Number), Q5 «Room photo» · Q6 «Additional comments» · «Fiber installation report…»: Q7–Q10 ·
«… (Copy)»: Q11 «Was the job completed successfully?», Q12 «Date of work.», Q13 «Which tasks were performed on site?»,
Q14 «Overall job status.»

| # | Відповідь | Правило | Видно | Сховано |
|---|---|---|---|---|
| FIB-1 | Q1 = Yes | — | усе | — |
| FIB-2 | Q1 = No | → Q6 | Q1, Q6–Q14 | секція «Room Information» (Q2–Q5) |
| FIB-3 | у «(Copy)»: Q11 = Yes | кінець | усе до Q11; у цьому екземплярі лише Q11; **«Repeat section» немає** | Q12–Q14 цього екземпляра |
| FIB-4 | Q11 = No | — | усе | — |

## Repeatable TWO sections with logic+questions (49 питань — найскладніше)

S1 (повт.) Q1–Q14 · S2 (повт.) Q15–Q28 · окремі Q29–Q35 «Question 1…7» · S3 (повт., без логіки) Q36–Q49. Назви
питань S1: «Q1 Enter the work order ID», «Q2 text…», «Q3 photo…», «Q4 Select the technician arrival time», «Q5 time…»,
«Q6 date…», «Q7 yes/no Question», «Q8 Radio Question», «Q9 test question», «Q10 photo question», «Q11 Checkbox Question»,
«Bad?», «Good?  Redirect to S2», «Problems?». S2 — те саме з префіксом «S2 », S3 — «S3 ».

**У межах екземпляра S1:**

| # | Відповідь | Правило | Сховано (лише в цьому екземплярі) |
|---|---|---|---|
| TWO-1 | «Q1 Enter the work order ID» = No | → Q3 | «Q2 text…» |
| TWO-2 | «Q4 Select the technician arrival time» = No | → Q6 | «Q5 time…» |
| TWO-3 | «Q7 yes/no Question» = No | → Q9 | «Q8 Radio Question» |
| TWO-4 | «Q8 Radio Question» = Option 2 Q8 | → Q10 | «Q9 test question» |
| TWO-5 | «Q8 Radio Question» = Option 3 Q8 | → Q11 | «Q9…», «Q10…» |
| TWO-6 | «Q8 Radio Question» = Option 4 Q8 | → Q14 | «Q9…» … «Good?  Redirect to S2» |
| TWO-7 | Yes / Option 1 у цих питаннях | → наступне | нічого |
| TWO-8 | екземпляр 1: «Q1…» = No; екземпляр 2: «Q1…» = Yes | — | «Q2 text…» сховане **лише в екземплярі 1** |

**З S1 в інші частини опитування:**

| # | Відповідь (у S1) | Правило | Видно | Сховано |
|---|---|---|---|---|
| TWO-9 | «Bad?» = No | кінець | S1 до «Bad?»; **«Repeat section» немає** | «Good?…», «Problems?», S2, Q29–Q35, S3 |
| TWO-10 | «Bad?» = Yes | → Q41 «S3 Q6 date Question» | S1 до «Bad?»; S3 — перший екземпляр **з «S3 Q6 date Question»** | «Good?…», «Problems?», S2, Q29–Q35, у S3 «S3 Q1…Q5» |
| TWO-11 | «Good?  Redirect to S2» = Yes | → Q15 (початок S2) | усе далі | «Problems?» |
| TWO-12 | «Good?  Redirect to S2» = No | → Q18 «S2 Q4 Select the technician arrival time» | S2 — перший екземпляр **з «S2 Q4…»** | «Problems?», у S2 «S2 Q1…Q3» |

**У S2 — потребує твого рішення:**

| # | Відповідь (у S2) | Правило | Що робить апка (код) | Твоє рішення |
|---|---|---|---|---|
| TWO-13 | «S2 Finish?» = Yes | кінець | S2 до «S2 Finish?»; далі все сховано | — (як кінець) |
| TWO-14 | «S2 Finish?» = No | → «S2 Bad?» (**назад**, у тому ж екземплярі) | ігнорує — нічого не ховає (**recon 8**) | як апка (правило «назад» — помилка шаблону) |
| TWO-15 | «S2 Good? if No than Redirect to S1 Q1» = No | → S1 Q1 (**назад**, в іншу секцію) | **recon 8:** у цьому екземплярі S2 ховається «S2 Finish?»; окремі питання і S3 **лишаються**; «Repeat section» — є | що має бути? |

## Photo Upload Test Survey, Repeatable Single section withOUT logic, stringsdf (порожнє) — логіки немає

Видно завжди все (у «stringsdf» — жодного питання).
