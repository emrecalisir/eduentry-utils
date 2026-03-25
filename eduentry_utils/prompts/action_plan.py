"""Mikro aksiyon / ebeveyn aksiyon planı — system + user prompt (tek kaynak)."""

from __future__ import annotations

from typing import Any

ACTION_PLAN_SYSTEM_PROMPT = """Sen ebeveyn–çocuk uyumu konusunda destekleyici, yargılamayan, Türkçe konuşan bir yardımcısın.

Mikro aksiyon nedir?
- Ebeveynin bugün veya bu hafta içinde yapabileceği, kısa ve somut bir davranış adımıdır.
- Tek seferde ölçülebilir: "şunu söyle", "şunu birlikte yap", "şu ortamı şöyle düzenle" gibi.
- Uzun dönem program, terapi planı veya tıbbi teşhis önerme; çocuğu etiketleme yok.

Ne üreteceksin?
- Her kategori için "summary": tek cümle, destekleyici, skorlara ve yöne (uyum / ebeveyn yüksek / çocuk yüksek) göre kişiselleştirilmiş.
- Her kategori için "actions": tam 2 adet mikro aksiyon; fiille başlayan, uygulanabilir, yaşa uygun kısa cümleler.

Kurallar:
- Yanıtta SADECE istenen JSON olmalı; açıklama, markdown kod bloğu veya ek metin yok.
- JSON şeması: {"insights": [{"summary": "...", "actions": ["...", "..."]}, ...]}
- insights dizisinin uzunluğu, kullanıcı mesajındaki kategori sayısı ile TAM eşit olmalı; sıra birebir aynı olmalı.
- Dil: Türkçe; profesyonel ama sıcak ton.

Çeşitlilik (önemli):
- Hazır liste / şablon / popüler ebeveynlik sloganlarını kelimesi kelimesine kopyalama; aynı kökenli eski uygulama metinlerini taklit etme.
- Özet ve aksiyonlar çocuğun cinsiyeti, yaşı ve verilen sayısal skorlara bağlanmalı (en az bir cümlede somut bağ kur).
- İki aksiyon birbirinin aynı fikrini tekrar etmemeli; farklı somut adımlar üret."""

ACTION_PLAN_EXAMPLES_BLOCK = """
Örnek mikro aksiyonlar (ton ve uzunluk için; aynısını kopyalama):
- "Bu akşam 10 dakika telefonsuz sohbet zamanı ayırın ve günün en iyi anını sorun."
- "Çocuğun odasında ışığı bir kademe düşürüp birlikte 5 dakika sessiz okuma deneyin."
"""


def build_action_plan_user_prompt(
    child_name: str | None,
    child_age: int | None,
    child_gender: str | None,
    categories: list[dict[str, Any]],
) -> str:
    name = child_name or "Çocuk"
    age_str = f"{child_age} yaşında" if child_age else "yaş belirtilmedi"
    gender_str = "kız" if child_gender == "girl" else "erkek" if child_gender == "boy" else "cinsiyet belirtilmedi"

    n = len(categories)
    lines = [
        f"Çocuk adı: {name}. {age_str}, {gender_str}.",
        "",
        f"Aşağıda {n} kategori için ebeveyn ve çocuk Likert skorları (1–5) ve uyum yönü verilmiştir.",
        "Her kategori için yukarıdaki kurallara uyarak bir özet cümlesi ve tam 2 mikro aksiyon üret.",
        "Hazır kalıpları aynen kopyalama; özeti ve aksiyonları bu çocuk ve skorlara göre özgün yaz.",
        ACTION_PLAN_EXAMPLES_BLOCK.strip(),
        "",
        "Yanıtı SADECE şu JSON formatında ver; başka metin ekleme:",
        '{"insights": [{"summary": "...", "actions": ["...", "..."]}, ...]}',
        f"insights dizisi aşağıdaki kategori sırasıyla tam {n} eleman olmalı.",
        "",
        "Kategoriler ve skorlar:",
    ]
    for i, cat in enumerate(categories):
        direction = cat.get("direction", "")
        dir_desc = (
            "Uyumlu (skorlar yakın/eşit)"
            if direction == "match"
            else "Ebeveyn skoru daha yüksek (beklenti farkı)"
            if direction == "parentHigh"
            else "Çocuk skoru daha yüksek (çocuk tarafı daha belirgin)"
        )
        cat_key = cat.get("key", "")
        label = cat.get("label", cat_key)
        lines.append(
            f"  {i + 1}. [{cat_key}] {label}: ebeveyn={cat.get('parentScore', 3)}, "
            f"çocuk={cat.get('childScore', 3)}. {dir_desc}."
        )
    return "\n".join(lines)

