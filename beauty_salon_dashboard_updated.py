from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, Field


app = FastAPI(
    title="Hi-Tech Beauty Salon Intelligence Dashboard",
    version="18.0.0",
    description="Professional beauty salon dashboard with popup chatbot, consultation scan, skin analysis, hair analysis, bridal styling, and Rybo the Friendly Bot-tique Assistant.",
)


# ============================================================
# ENUMS
# ============================================================

class Language(str, Enum):
    english = "english"
    tamil = "tamil"


class SkinType(str, Enum):
    oily = "oily"
    dry = "dry"
    combination = "combination"
    sensitive = "sensitive"
    normal = "normal"
    acne_prone = "acne_prone"


class HairType(str, Enum):
    straight = "straight"
    wavy = "wavy"
    curly = "curly"
    coily = "coily"


class HairCondition(str, Enum):
    healthy = "healthy"
    dry = "dry"
    damaged = "damaged"
    thinning = "thinning"
    dandruff = "dandruff"
    hair_fall = "hair_fall"
    frizzy = "frizzy"


class FaceShape(str, Enum):
    oval = "oval"
    round = "round"
    square = "square"
    heart = "heart"
    diamond = "diamond"
    oblong = "oblong"


# ============================================================
# MODELS
# ============================================================

class HealthResponse(BaseModel):
    status: str
    service: str
    time: datetime


class ChatRequest(BaseModel):
    customer_name: str = "Guest"
    language: Language = Language.tamil
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    customer_name: str
    language: Language
    intent: str
    sentiment: str
    reply: str
    suggested_services: List[str] = []
    next_step: str


class ConsultationRequest(BaseModel):
    customer_name: str
    language: Language = Language.english
    face_shape: FaceShape
    skin_type: SkinType
    hair_type: HairType
    hair_condition: HairCondition
    bridal_interest: bool = False
    concern: Optional[str] = None
    budget_inr: Optional[float] = None


class ConsultationResponse(BaseModel):
    customer_name: str
    face_shape: str
    skin_type: str
    hair_type: str
    hair_condition: str
    recommended_haircuts: List[str]
    recommended_hairstyles: List[str]
    recommended_hair_treatments: List[str]
    recommended_hair_colors: List[str]
    recommended_facials: List[str]
    recommended_additional_services: List[str]
    bridal_recommendations: List[str]
    warnings: List[str]
    report_summary: str


class SkinAnalysisRequest(BaseModel):
    customer_name: str
    skin_type: SkinType
    acne_score: int = Field(..., ge=0, le=10)
    pigmentation_score: int = Field(..., ge=0, le=10)
    dryness_score: int = Field(..., ge=0, le=10)
    sensitivity_score: int = Field(..., ge=0, le=10)
    tanning_score: int = Field(..., ge=0, le=10)


class SkinAnalysisResponse(BaseModel):
    customer_name: str
    skin_health_index: float
    detected_issues: List[str]
    recommended_facials: List[str]
    recommended_homecare: List[str]
    warnings: List[str]
    salon_workflow: List[str]
    ai_summary: str


class HairAnalysisRequest(BaseModel):
    customer_name: str
    face_shape: FaceShape
    hair_type: HairType
    hair_condition: HairCondition
    dandruff_score: int = Field(..., ge=0, le=10)
    hair_fall_score: int = Field(..., ge=0, le=10)
    breakage_score: int = Field(..., ge=0, le=10)
    scalp_oiliness: int = Field(..., ge=0, le=10)
    chemical_history: bool = False


class HairAnalysisResponse(BaseModel):
    customer_name: str
    hair_health_index: float
    detected_issues: List[str]
    recommended_treatments: List[str]
    recommended_hairstyles: List[str]
    recommended_haircuts: List[str]
    recommended_hair_colors: List[str]
    recommended_homecare: List[str]
    warnings: List[str]
    salon_workflow: List[str]
    ai_summary: str


class BridalRequest(BaseModel):
    customer_name: str
    saree_color: str
    saree_fabric: str
    saree_pattern: str
    wants_modern_touch: bool = False


class BridalResponse(BaseModel):
    customer_name: str
    palette_match: str
    recommended_jewelry: List[str]
    recommended_hairstyles: List[str]
    priority_looks: List[Dict[str, str]]
    message: str


# ============================================================
# MEMORY / DEMO METRICS
# ============================================================

CHAT_LOGS: List[Dict[str, str]] = []
CONSULT_LOGS: List[Dict[str, str]] = []
SKIN_LOGS: List[Dict[str, str]] = []
HAIR_LOGS: List[Dict[str, str]] = []
BRIDAL_LOGS: List[Dict[str, str]] = []


# ============================================================
# KNOWLEDGE BASE
# ============================================================

SERVICE_CATALOG: Dict[str, List[str]] = {
    "facials": [
        "Hydra Glow Facial",
        "Acne Control Facial",
        "Oil Balance Facial",
        "Brightening Facial",
        "Sensitive Skin Soothing Facial",
        "Tan Removal Facial",
        "Bridal Radiance Facial",
        "Moisture Barrier Facial",
        "Purifying Facial",
    ],
    "haircuts": [
        "Layer Cut",
        "Feather Cut",
        "Bob Cut",
        "Soft Lob",
        "Face-Framing Cut",
        "Long U Cut",
        "Textured Cut",
    ],
    "hair_treatments": [
        "Hot Oil Hair Massage",
        "Deep Nourish Hair Spa",
        "Protein Repair Hair Therapy",
        "Anti-Dandruff Scalp Therapy",
        "Scalp Strengthening Massage",
        "Root Activation Therapy",
        "Anti-Hair Fall Spa",
        "Curl Moisture Restore Therapy",
        "Color Protection Ritual",
        "Pre-Color Bond Shield Therapy",
    ],
    "hair_colors": [
        "Soft Chocolate Brown",
        "Caramel Balayage",
        "Espresso Brown",
        "Burgundy Glow",
        "Mahogany Brown",
        "Copper Cinnamon",
        "Honey Highlights",
        "Mocha Melt",
        "Wine Plum Tint",
        "Golden Brown Gloss",
    ],
    "nails_and_feet": [
        "Classic Manicure",
        "Spa Manicure",
        "Classic Pedicure",
        "Luxury Spa Pedicure",
        "Foot Reflexology Massage",
    ],
    "bridal": [
        "Bridal Trial Session",
        "HD Bridal Makeup",
        "Airbrush Bridal Makeup",
        "Bridal Skin Prep Package",
        "Bridal Manicure + Pedicure",
    ],
    "massage": [
        "Head, Neck & Shoulder Massage",
        "Aroma Relax Massage",
        "Foot Reflexology Massage",
        "Scalp Relaxation Massage",
    ],
}


# ============================================================
# HELPERS
# ============================================================

def unique_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


def lang_text(lang: Language, english_text: str, tamil_text: str) -> str:
    return tamil_text if lang == Language.tamil else english_text


def recommend_haircuts(face_shape: FaceShape) -> List[str]:
    mapping = {
        FaceShape.round: ["Feather Cut", "Long Layers", "Soft Lob", "Face-Framing Cut"],
        FaceShape.oval: ["Bob Cut", "Layer Cut", "Long U Cut", "Soft Waves Cut"],
        FaceShape.square: ["Soft Lob", "Textured Layers", "Side-Swept Cut", "Layered Waves"],
        FaceShape.heart: ["Long U Cut", "Side Layers", "Soft Lob", "Chin-Length Volume Cut"],
        FaceShape.diamond: ["Textured Bob", "Shoulder Lob", "Soft Fringe Layers", "Volume Side Cut"],
        FaceShape.oblong: ["Curtain Fringe Cut", "Layered Lob", "Shoulder Waves", "Chin Soft Layers"],
    }
    return mapping.get(face_shape, ["Layer Cut", "Face-Framing Cut"])


def recommend_hairstyles(face_shape: FaceShape) -> List[str]:
    mapping = {
        FaceShape.round: ["Crown Volume Waves", "Side-Part Curls", "Long Straight Layers", "High Pony with Lift"],
        FaceShape.oval: ["Soft Curls", "Sleek Bun", "Beach Waves", "Straight Open Hair"],
        FaceShape.square: ["Soft Curls", "Loose Waves", "Side Bun", "Textured Blowout"],
        FaceShape.heart: ["Side-Swept Curls", "Low Bun", "Soft Lob Styling", "Loose Volume Ends"],
        FaceShape.diamond: ["Textured Bob Styling", "Shoulder Waves", "Side Puff Bun", "Soft Fringe Look"],
        FaceShape.oblong: ["Curtain Fringe Waves", "Shoulder Volume Curls", "Layered Blowout", "Soft Open Hair"],
    }
    return mapping.get(face_shape, ["Soft Blow Dry", "Elegant Open Hair"])


def recommend_hair_treatments(hair_condition: HairCondition, hair_type: HairType, chemical_history: bool = False) -> List[str]:
    suggestions: List[str] = []

    if hair_condition in [HairCondition.dry, HairCondition.damaged, HairCondition.frizzy]:
        suggestions.extend(["Hot Oil Hair Massage", "Deep Nourish Hair Spa", "Protein Repair Hair Therapy"])
    elif hair_condition in [HairCondition.hair_fall, HairCondition.thinning]:
        suggestions.extend(["Scalp Strengthening Massage", "Root Activation Therapy", "Anti-Hair Fall Spa"])
    elif hair_condition == HairCondition.dandruff:
        suggestions.extend(["Anti-Dandruff Scalp Therapy", "Tea Tree Scalp Massage", "Scalp Purifying Treatment"])
    else:
        suggestions.extend(["Weekly Nourish Hair Massage", "Relaxing Head Spa", "Maintenance Hair Spa"])

    if chemical_history:
        suggestions.extend(["Pre-Color Bond Shield Therapy", "Color Protection Ritual"])

    if hair_type == HairType.curly:
        suggestions.append("Curl Moisture Restore Therapy")
    elif hair_type == HairType.straight:
        suggestions.append("Lightweight Root Care Massage")
    elif hair_type == HairType.wavy:
        suggestions.append("Wave Texture Nourish Spa")

    return unique_keep_order(suggestions)[:6]


def recommend_hair_colors(face_shape: FaceShape, hair_condition: HairCondition, skin_type: Optional[SkinType] = None) -> List[str]:
    colors: List[str] = []

    if face_shape == FaceShape.round:
        colors.extend(["Caramel Balayage", "Mocha Melt", "Honey Highlights"])
    elif face_shape == FaceShape.oval:
        colors.extend(["Soft Chocolate Brown", "Copper Cinnamon", "Golden Brown Gloss"])
    elif face_shape == FaceShape.square:
        colors.extend(["Mahogany Brown", "Caramel Balayage", "Espresso Brown"])
    elif face_shape == FaceShape.heart:
        colors.extend(["Honey Highlights", "Soft Chocolate Brown", "Wine Plum Tint"])
    elif face_shape == FaceShape.diamond:
        colors.extend(["Burgundy Glow", "Mocha Melt", "Golden Brown Gloss"])
    else:
        colors.extend(["Espresso Brown", "Caramel Balayage", "Copper Cinnamon"])

    if hair_condition in [HairCondition.damaged, HairCondition.dry]:
        colors = [c for c in colors if c not in ["Wine Plum Tint", "Burgundy Glow"]]
        colors.extend(["Soft Chocolate Brown", "Espresso Brown"])
    if hair_condition in [HairCondition.hair_fall, HairCondition.thinning]:
        colors = [c for c in colors if c not in ["Copper Cinnamon"]]
        colors.extend(["Golden Brown Gloss"])
    if skin_type == SkinType.sensitive:
        colors.extend(["Ammonia-Free Natural Brown"])
    if skin_type == SkinType.oily:
        colors.extend(["Cool Mocha Brown"])

    return unique_keep_order(colors)[:5]


def recommend_facials(skin_type: SkinType, bridal_interest: bool = False) -> List[str]:
    if bridal_interest:
        return ["Bridal Radiance Facial", "Hydra Glow Facial", "Brightening Tan Removal Facial"]

    mapping = {
        SkinType.oily: ["Acne Control Facial", "Oil Balance Facial", "Deep Clean Pore Facial"],
        SkinType.dry: ["Hydra Glow Facial", "Milk Cream Nourish Facial", "Moisture Barrier Facial"],
        SkinType.combination: ["Hydra Balance Facial", "Brightening Facial", "Pore & Glow Facial"],
        SkinType.sensitive: ["Sensitive Skin Soothing Facial", "Barrier Calm Facial", "Redness Relief Facial"],
        SkinType.normal: ["Maintenance Glow Facial", "Hydra Glow Facial", "Brightening Facial"],
        SkinType.acne_prone: ["Acne Control Facial", "Purifying Facial", "Calming Recovery Facial"],
    }
    return mapping.get(skin_type, ["Hydra Glow Facial", "Maintenance Glow Facial"])


def additional_services(bridal_interest: bool) -> List[str]:
    services = [
        "Classic Manicure",
        "Spa Manicure",
        "Classic Pedicure",
        "Luxury Spa Pedicure",
        "Foot Reflexology Massage",
        "Head, Neck & Shoulder Massage",
        "Aroma Relax Massage",
    ]
    if bridal_interest:
        services.extend([
            "Bridal Manicure",
            "Bridal Pedicure",
            "HD Bridal Makeup",
            "Airbrush Bridal Makeup",
            "Bridal Trial Session",
        ])
    return services


def bridal_recommendations(enabled: bool) -> List[str]:
    if not enabled:
        return []
    return [
        "Bridal Trial Session",
        "HD Bridal Makeup",
        "Airbrush Bridal Makeup",
        "Bridal Skin Prep Package",
        "Bridal Manicure + Pedicure",
    ]


def consultation_summary(name: str, language: Language, facials: List[str], haircuts: List[str], colors: List[str]) -> str:
    if language == Language.tamil:
        return (
            f"வணக்கம் {name}, உங்கள் face shape மற்றும் skin/hair profile அடிப்படையில் "
            f"பரிந்துரைக்கப்படும் hairstyle: {', '.join(haircuts[:2])}. "
            f"பரிந்துரைக்கப்படும் facial: {', '.join(facials[:2])}. "
            f"Hair color suggestion: {', '.join(colors[:2])}. "
            "மேலும் bridal, manicure, pedicure, foot massage மற்றும் hair spa சேவைகளும் உங்களுக்கு ஏற்றவை."
        )
    return (
        f"Hello {name}, based on your face shape and skin/hair profile, recommended haircut options are "
        f"{', '.join(haircuts[:2])}, facial options are {', '.join(facials[:2])}, and hair color options are "
        f"{', '.join(colors[:2])}. We also recommend manicure, pedicure, foot massage, and premium salon care."
    )


def is_thanks_message(text: str) -> bool:
    thanks_terms = ["thanks", "thank you", "thx", "thankyou", "nandri", "நன்றி"]
    msg = text.lower().strip()
    return any(term in msg for term in thanks_terms)


# ============================================================
# CHATBOT
# ============================================================

def create_chat_reply(req: ChatRequest) -> ChatResponse:
    message = req.message.lower().strip()

    if is_thanks_message(message):
        return ChatResponse(
            customer_name=req.customer_name,
            language=req.language,
            intent="gratitude",
            sentiment="warm",
            reply=lang_text(
                req.language,
                f"பரவாயில்லை {req.customer_name}. You’re welcome. I’m here whenever you need beauty guidance or magical styling ideas.",
                f"பரவாயில்லை {req.customer_name}. Beauty guidance அல்லது styling idea எப்போது வேண்டுமானாலும் நான் உதவ தயாராக இருக்கிறேன்.",
            ),
            suggested_services=[],
            next_step=lang_text(
                req.language,
                "Ask me about facial, haircut, hair color, bridal, manicure, or pedicure anytime.",
                "Facial, haircut, hair color, bridal, manicure அல்லது pedicure பற்றி எப்போது வேண்டுமானாலும் கேளுங்கள்.",
            ),
        )

    bridal_keywords = ["bridal", "wedding", "makeup", "saree", "reception", "engagement", "bride", "bridal package"]
    hair_keywords = ["hair", "haircut", "hairstyle", "spa", "dandruff", "frizz", "style", "hair fall", "scalp", "trim", "smoothening", "straightening", "curl"]
    hair_color_keywords = ["hair color", "hair colouring", "hair coloring", "colour", "color", "highlights", "balayage", "tint", "global color"]
    skin_keywords = ["skin", "facial", "glow", "pigmentation", "tan", "acne", "cleanup", "dry skin", "oily skin", "sensitive skin"]
    nails_feet_keywords = ["pedicure", "manicure", "foot", "massage", "nail", "feet", "heel", "reflexology", "head massage"]
    pricing_keywords = ["price", "cost", "charges", "rate", "package", "budget"]
    greeting_keywords = ["hi", "hello", "hey", "vanakkam", "good morning", "good evening", "ஹலோ", "வணக்கம்"]

    has_bridal = any(k in message for k in bridal_keywords)
    has_hair = any(k in message for k in hair_keywords)
    has_hair_color = any(k in message for k in hair_color_keywords)
    has_skin = any(k in message for k in skin_keywords)
    has_nails_feet = any(k in message for k in nails_feet_keywords)
    has_pricing = any(k in message for k in pricing_keywords)
    has_greeting = any(k in message for k in greeting_keywords)

    suggested_services: List[str] = []
    intent_parts: List[str] = []

    if has_bridal:
        intent_parts.append("bridal")
        suggested_services.extend(SERVICE_CATALOG["bridal"][:4])

    if has_skin:
        intent_parts.append("skin")
        suggested_services.extend(SERVICE_CATALOG["facials"][:4])

    if has_hair:
        intent_parts.append("hair")
        suggested_services.extend(["Layer Cut", "Feather Cut", "Hot Oil Hair Massage", "Deep Nourish Hair Spa"])

    if has_hair_color:
        intent_parts.append("hair_color")
        suggested_services.extend(["Global Hair Color", "Balayage", "Highlights", "Color Protection Ritual"])

    if has_nails_feet:
        intent_parts.append("service")
        suggested_services.extend(["Classic Pedicure", "Spa Manicure", "Foot Reflexology Massage"])

    suggested_services = unique_keep_order(suggested_services)[:8]

    if has_greeting and not (has_bridal or has_skin or has_hair or has_hair_color or has_nails_feet or has_pricing):
        intent = "greeting"
        sentiment = "positive"
        reply = (
            f"வணக்கம் {req.customer_name}. நான் Rybo, உங்கள் friendly Bot-tique assistant. "
            "Facial, haircut suggestion, hair color, bridal makeup, manicure, pedicure, hair spa மற்றும் massage services பற்றி உதவ முடியும். "
            "உங்களுக்கு என்ன வேண்டும் என்று சொல்லுங்கள்."
        )
        next_step = "Facial, haircut, hair color, bridal makeup, manicure, pedicure அல்லது massage போன்ற உங்கள் தேவையை சொல்லுங்கள்."

    elif has_hair_color and has_hair:
        intent = "hair_and_color_support"
        sentiment = "creative"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. I can help with both haircut and hair color suggestions. Based on face shape and hair condition, we can match a haircut, styling pattern, and color like caramel balayage, mocha melt, honey highlights, soft chocolate brown, or burgundy glow.",
            f"வணக்கம் {req.customer_name}. Haircut மற்றும் hair color இரண்டிற்கும் உதவ முடியும். Face shape மற்றும் hair condition அடிப்படையில் haircut, styling pattern மற்றும் caramel balayage, mocha melt, honey highlights, soft chocolate brown அல்லது burgundy glow போன்ற color options பரிந்துரைக்கலாம்.",
        )
        next_step = lang_text(
            req.language,
            "Use Hair Report for haircut, treatment, and color suggestions together.",
            "Haircut, treatment, color suggestion அனைத்திற்கும் Hair Report பயன்படுத்தவும்.",
        )

    elif has_skin and has_hair and has_pricing:
        intent = "skin_hair_pricing"
        sentiment = "helpful"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. For your facial and haircut requirement, I can guide you with service suggestions and pricing direction. We provide glow, acne-control, brightening, tan-removal, and sensitive-skin facials. For hair, we provide haircut, hairstyle, hair spa, scalp therapy, dandruff care, hair fall support, and hair coloring options. Final cost depends on the service type and concern level.",
            f"வணக்கம் {req.customer_name}. உங்கள் facial மற்றும் haircut தேவைக்கு service suggestion மற்றும் pricing guidance தர முடியும். Glow, acne-control, brightening, tan-removal, sensitive-skin facial சேவைகள் உள்ளன. Hair side-ல் haircut, hairstyle, hair spa, scalp therapy, dandruff care, hair fall support மற்றும் hair coloring options உள்ளன. இறுதி கட்டணம் service மற்றும் concern level அடிப்படையில் மாறும்.",
        )
        next_step = lang_text(
            req.language,
            "Use Consultation Scan for a more personalized service combination.",
            "மேலும் personalized service combination-க்கு Consultation Scan பயன்படுத்தவும்.",
        )

    elif has_skin and has_hair:
        intent = "skin_hair_support"
        sentiment = "supportive"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. I can help with both facial and haircut requirements. Based on skin concern, I can suggest hydrating, acne-control, glow, brightening, tan-removal, or soothing facials. Based on face shape and hair condition, I can suggest haircut, hairstyle, hair spa, scalp therapy, massage options, and suitable hair color ideas.",
            f"வணக்கம் {req.customer_name}. Facial மற்றும் haircut இரண்டிற்கும் உதவ முடியும். Skin concern அடிப்படையில் hydrating, acne-control, glow, brightening, tan-removal அல்லது soothing facial பரிந்துரைக்கலாம். Face shape மற்றும் hair condition அடிப்படையில் haircut, hairstyle, hair spa, scalp therapy, massage options மற்றும் suitable hair color ideas பரிந்துரைக்கலாம்.",
        )
        next_step = lang_text(
            req.language,
            "Use Consultation Scan for a combined facial and haircut report.",
            "முழு facial மற்றும் haircut report-க்கு Consultation Scan பயன்படுத்தவும்.",
        )

    elif has_bridal and has_skin:
        intent = "bridal_skin_support"
        sentiment = "positive"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. I can help with bridal makeup and bridal skin preparation. We offer bridal trial, HD bridal makeup, airbrush bridal makeup, bridal facials, skin prep packages, manicure, pedicure, saree-based styling, and elegant bridal hair color finishing suggestions.",
            f"வணக்கம் {req.customer_name}. Bridal makeup மற்றும் bridal skin preparation இரண்டிற்கும் உதவ முடியும். Bridal trial, HD bridal makeup, airbrush bridal makeup, bridal facial, skin prep package, manicure, pedicure, saree-based styling மற்றும் bridal hair color finishing suggestion சேவைகள் உள்ளன.",
        )
        next_step = lang_text(
            req.language,
            "Use Bridal Stylist and Skin Report for full bridal recommendations.",
            "முழு bridal recommendation-க்கு Bridal Stylist மற்றும் Skin Report பயன்படுத்தவும்.",
        )

    elif has_bridal:
        intent = "bridal_support"
        sentiment = "positive"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. I can help with bridal trial, HD bridal makeup, airbrush bridal makeup, bridal facial, saree styling, manicure, pedicure, complete bridal preparation, and bridal hair styling ideas.",
            f"வணக்கம் {req.customer_name}. Bridal trial, HD bridal makeup, airbrush bridal makeup, bridal facial, saree styling, manicure, pedicure, complete bridal preparation மற்றும் bridal hair styling ideas-க்கு உதவ முடியும்.",
        )
        next_step = lang_text(
            req.language,
            "Use Bridal Stylist for bridal look suggestions.",
            "Bridal look suggestion-க்கு Bridal Stylist பயன்படுத்தவும்.",
        )

    elif has_skin:
        intent = "skin_support"
        sentiment = "helpful"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. I can help with facial and skin care enquiries. Depending on the concern, I can recommend hydrating, acne-control, glow, brightening, tan-removal, or sensitive-skin facials.",
            f"வணக்கம் {req.customer_name}. Facial மற்றும் skin care enquiry-க்கு உதவ முடியும். Concern அடிப்படையில் hydrating, acne-control, glow, brightening, tan-removal அல்லது sensitive-skin facial பரிந்துரைக்கலாம்.",
        )
        next_step = lang_text(
            req.language,
            "Use Skin Report to generate a facial recommendation report.",
            "Facial recommendation report-க்கு Skin Report பயன்படுத்தவும்.",
        )

    elif has_hair or has_hair_color:
        intent = "hair_support"
        sentiment = "creative"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. I can help with haircut, hairstyle, hair spa, scalp therapy, anti-dandruff treatment, hair fall care, and hair coloring options such as balayage, highlights, mocha, caramel, chocolate brown, or burgundy tones based on face shape and hair condition.",
            f"வணக்கம் {req.customer_name}. Face shape மற்றும் hair condition அடிப்படையில் haircut, hairstyle, hair spa, scalp therapy, anti-dandruff treatment, hair fall care மற்றும் balayage, highlights, mocha, caramel, chocolate brown, burgundy போன்ற hair coloring options பரிந்துரைக்கலாம்.",
        )
        next_step = lang_text(
            req.language,
            "Use Hair Report for detailed haircut, treatment, and color recommendations.",
            "விரிவான haircut, treatment, color recommendation-க்கு Hair Report பயன்படுத்தவும்.",
        )

    elif has_nails_feet:
        intent = "service_support"
        sentiment = "positive"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. I can help with pedicure, manicure, foot reflexology, head massage, and relaxation services. These can also be added as premium salon add-ons.",
            f"வணக்கம் {req.customer_name}. Pedicure, manicure, foot reflexology, head massage மற்றும் relaxation services பற்றிய தகவல் வழங்க முடியும். இவை premium add-on service-களாகவும் சேர்க்கலாம்.",
        )
        next_step = lang_text(
            req.language,
            "Tell me whether you need regular care, premium care, or bridal add-ons.",
            "Regular care, premium care அல்லது bridal add-on எது வேண்டும் என்று சொல்லுங்கள்.",
        )

    elif has_pricing:
        intent = "pricing_support"
        sentiment = "neutral"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. Pricing depends on the service type, concern level, and whether you want regular, premium, color, or bridal packages. I can first help identify the right service combination for you.",
            f"வணக்கம் {req.customer_name}. கட்டணம் service வகை, concern level, regular, color, premium அல்லது bridal package அடிப்படையில் மாறும். முதலில் உங்களுக்கு சரியான service combination-ஐ கண்டுபிடிக்க உதவுகிறேன்.",
        )
        next_step = lang_text(
            req.language,
            "Tell me whether you want facial, haircut, hair color, bridal makeup, manicure, pedicure, or massage.",
            "Facial, haircut, hair color, bridal makeup, manicure, pedicure அல்லது massage ஆகியவற்றில் எது வேண்டும் என்று சொல்லுங்கள்.",
        )

    else:
        intent = "general_support"
        sentiment = "neutral"
        reply = lang_text(
            req.language,
            f"வணக்கம் {req.customer_name}. I can help with facials, haircut suggestions, hair spa, hair coloring, dandruff care, bridal makeup, manicure, pedicure, and massage services. Tell me your requirement and I will guide you properly.",
            f"வணக்கம் {req.customer_name}. Facial, haircut suggestion, hair spa, hair coloring, dandruff care, bridal makeup, manicure, pedicure மற்றும் massage services-க்கு உதவ முடியும். உங்கள் requirement-ஐ சொல்லுங்கள், நான் சரியாக வழிகாட்டுகிறேன்.",
        )
        next_step = lang_text(
            req.language,
            "Describe your requirement like facial, haircut, hair color, hair spa, bridal, manicure, pedicure, or massage.",
            "Facial, haircut, hair color, hair spa, bridal, manicure, pedicure அல்லது massage போன்ற requirement-ஐ சொல்லுங்கள்.",
        )

    if not suggested_services:
        suggested_services = ["Hydra Glow Facial", "Layer Cut", "Global Hair Color"]

    response = ChatResponse(
        customer_name=req.customer_name,
        language=req.language,
        intent="_".join(intent_parts) if intent_parts else intent,
        sentiment=sentiment,
        reply=reply,
        suggested_services=suggested_services,
        next_step=next_step,
    )
    CHAT_LOGS.append({"customer_name": req.customer_name, "intent": response.intent, "time": datetime.utcnow().isoformat()})
    return response


# ============================================================
# ANALYSIS REPORTS
# ============================================================

def build_consultation(req: ConsultationRequest) -> ConsultationResponse:
    haircuts = recommend_haircuts(req.face_shape)
    hairstyles = recommend_hairstyles(req.face_shape)
    treatments = recommend_hair_treatments(req.hair_condition, req.hair_type)
    hair_colors = recommend_hair_colors(req.face_shape, req.hair_condition, req.skin_type)
    facials = recommend_facials(req.skin_type, req.bridal_interest)

    warnings: List[str] = []
    if req.hair_condition in [HairCondition.damaged, HairCondition.dry]:
        warnings.append("Avoid frequent bleach or strong color processing until hair moisture and strength improve.")
    if req.hair_condition in [HairCondition.hair_fall, HairCondition.thinning]:
        warnings.append("Scalp-strengthening treatment is recommended before chemical styling or intense coloring.")
    if req.skin_type == SkinType.sensitive:
        warnings.append("Patch test recommended before facial actives and hair color application.")
    if req.skin_type == SkinType.acne_prone:
        warnings.append("Avoid aggressive scrubbing and heavy comedogenic makeup.")

    response = ConsultationResponse(
        customer_name=req.customer_name,
        face_shape=req.face_shape.value,
        skin_type=req.skin_type.value,
        hair_type=req.hair_type.value,
        hair_condition=req.hair_condition.value,
        recommended_haircuts=haircuts,
        recommended_hairstyles=hairstyles,
        recommended_hair_treatments=treatments,
        recommended_hair_colors=hair_colors,
        recommended_facials=facials,
        recommended_additional_services=additional_services(req.bridal_interest),
        bridal_recommendations=bridal_recommendations(req.bridal_interest),
        warnings=warnings,
        report_summary=consultation_summary(req.customer_name, req.language, facials, haircuts, hair_colors),
    )
    CONSULT_LOGS.append({"customer_name": req.customer_name, "time": datetime.utcnow().isoformat()})
    return response


def analyze_skin(req: SkinAnalysisRequest) -> SkinAnalysisResponse:
    issues: List[str] = []
    facials = recommend_facials(req.skin_type)
    homecare: List[str] = []
    warnings: List[str] = []

    severity_total = req.acne_score + req.pigmentation_score + req.dryness_score + req.sensitivity_score + req.tanning_score
    health_index = round(max(0.0, 100 - (severity_total * 1.8)), 2)

    if req.acne_score >= 6:
        issues.append("Acne or breakout tendency detected")
        homecare.append("Use gentle oil-control cleanser and non-comedogenic moisturizer")
        warnings.append("Avoid harsh scrubs and heavy pore-clogging products")
    if req.pigmentation_score >= 6:
        issues.append("Pigmentation or uneven tone detected")
        homecare.append("Use sunscreen and brightening serum regularly")
    if req.dryness_score >= 6:
        issues.append("Dryness and dehydration detected")
        homecare.append("Use ceramide or hyaluronic acid-based moisturizer")
        warnings.append("Avoid over-exfoliation")
    if req.sensitivity_score >= 6:
        issues.append("Skin sensitivity or barrier weakness detected")
        homecare.append("Use fragrance-free calming skincare")
        warnings.append("Patch testing recommended for active ingredients")
    if req.tanning_score >= 6:
        issues.append("Tanning detected")
        homecare.append("Reapply sunscreen and use tan-recovery facial care")

    if not issues:
        issues.append("Skin condition is manageable with maintenance care")
    if not homecare:
        homecare.append("Maintain cleanse, moisturize, and sunscreen routine")
    if not warnings:
        warnings.append("Follow post-facial care and hydration routine")

    workflow = [
        "Profile review",
        "Skin concern scoring",
        "AI recommendation of suitable facial",
        "Warnings and sensitivity review",
        "Homecare guidance",
        "Salon treatment plan",
    ]

    summary = (
        f"{req.customer_name}'s skin analysis suggests {', '.join(facials[:2])} as the best facial options "
        f"based on {req.skin_type.value} skin and detected concern levels."
    )

    response = SkinAnalysisResponse(
        customer_name=req.customer_name,
        skin_health_index=health_index,
        detected_issues=issues,
        recommended_facials=facials,
        recommended_homecare=homecare,
        warnings=warnings,
        salon_workflow=workflow,
        ai_summary=summary,
    )
    SKIN_LOGS.append({"customer_name": req.customer_name, "time": datetime.utcnow().isoformat()})
    return response


def analyze_hair(req: HairAnalysisRequest) -> HairAnalysisResponse:
    issues: List[str] = []
    treatments = recommend_hair_treatments(req.hair_condition, req.hair_type, req.chemical_history)
    hairstyles = recommend_hairstyles(req.face_shape)
    haircuts = recommend_haircuts(req.face_shape)
    hair_colors = recommend_hair_colors(req.face_shape, req.hair_condition)
    homecare: List[str] = []
    warnings: List[str] = []

    score = req.dandruff_score + req.hair_fall_score + req.breakage_score + req.scalp_oiliness
    if req.chemical_history:
        score += 4
    health_index = round(max(0.0, 100 - (score * 2.1)), 2)

    if req.dandruff_score >= 6:
        issues.append("Dandruff or scalp flaking detected")
        homecare.append("Use a gentle anti-dandruff shampoo")
        warnings.append("Avoid heavy oily buildup on irritated scalp")
    if req.hair_fall_score >= 6:
        issues.append("Hair fall tendency detected")
        homecare.append("Use scalp-strengthening serum and avoid tight hairstyles")
        warnings.append("Persistent severe hair fall may need clinical review")
    if req.breakage_score >= 6:
        issues.append("Hair breakage and weakness detected")
        homecare.append("Use leave-in conditioner and reduce heat exposure")
        warnings.append("Avoid bleach-heavy or repeated harsh coloring until hair strength improves")
    if req.scalp_oiliness >= 7:
        issues.append("High scalp oiliness detected")
        homecare.append("Use balancing shampoo and avoid frequent heavy oils")
    if req.chemical_history:
        issues.append("Chemical stress history detected")
        warnings.append("Delay additional harsh chemical processing until recovery improves")
        homecare.append("Use protein-moisture balanced repair care")
        homecare.append("Use sulfate-light color-safe shampoo if hair is colored")

    if not issues:
        issues.append("Hair condition is manageable with maintenance care")
    if not homecare:
        homecare.append("Maintain regular trimming, scalp hygiene, and nourishing hair care")
    if not warnings:
        warnings.append("Use heat protectant before styling and color protection after coloring")

    workflow = [
        "Hair profile review",
        "Scalp and strand scoring",
        "AI recommendation of treatment and haircut",
        "Hair color matching based on face shape and condition",
        "Homecare guidance",
        "Salon service plan",
    ]

    summary = (
        f"{req.customer_name}'s hair analysis recommends {', '.join(treatments[:2])}, "
        f"haircuts like {', '.join(haircuts[:2])}, and colors such as {', '.join(hair_colors[:2])} "
        f"based on hair condition and face shape."
    )

    response = HairAnalysisResponse(
        customer_name=req.customer_name,
        hair_health_index=health_index,
        detected_issues=issues,
        recommended_treatments=treatments,
        recommended_hairstyles=hairstyles,
        recommended_haircuts=haircuts,
        recommended_hair_colors=hair_colors,
        recommended_homecare=homecare,
        warnings=warnings,
        salon_workflow=workflow,
        ai_summary=summary,
    )
    HAIR_LOGS.append({"customer_name": req.customer_name, "time": datetime.utcnow().isoformat()})
    return response


def analyze_bridal(req: BridalRequest) -> BridalResponse:
    color = req.saree_color.lower().strip()
    palette_map = {
        "red": "Classic Royal Bridal Palette",
        "maroon": "Deep Regal Bridal Palette",
        "green": "Heritage South Indian Bridal Palette",
        "pink": "Soft Romantic Bridal Palette",
        "gold": "Luxury Reception Bridal Palette",
    }
    jewelry_map = {
        "red": ["Gold Temple Jewelry", "Statement Bangles", "Bridal Maang Tikka"],
        "maroon": ["Antique Gold Jewelry", "Kundan Layers", "Matha Patti"],
        "green": ["Matte Gold with Emerald Stones", "Temple Necklace", "Bridal Jhumkas"],
        "pink": ["Rose Gold Jewelry", "Pearl Set", "Soft Stone Earrings"],
        "gold": ["Antique Gold Jewelry", "Grand Choker", "Reception Earrings"],
    }

    palette = palette_map.get(color, "Balanced Festive Bridal Palette")
    jewelry = jewelry_map.get(color, ["Classic Gold Jewelry", "Statement Bangles", "Elegant Earrings"])

    hairstyles = [
        "Center-Parted Bridal Bun",
        "Braided Floral Bun",
        "Soft Reception Curls" if req.wants_modern_touch else "Traditional Jasmine Bun",
    ]

    looks = [
        {
            "priority": "P1",
            "title": "Royal Traditional Bride",
            "makeup_style": "Full bridal glam with classic eye definition",
            "hairstyle": "Center-parted bun with flowers",
        },
        {
            "priority": "P2",
            "title": "Elegant Temple Bride",
            "makeup_style": "Soft matte base with bronze eye look",
            "hairstyle": "Braided bun with temple accessories",
        },
        {
            "priority": "P3",
            "title": "Modern Reception Bride",
            "makeup_style": "Radiant skin-focused glam",
            "hairstyle": "Soft curls or textured bun",
        },
    ]

    message = (
        f"{req.customer_name}'s bridal styling is matched to {palette}. "
        f"Recommended jewelry and hairstyle have been generated based on saree color, fabric, and styling direction."
    )

    response = BridalResponse(
        customer_name=req.customer_name,
        palette_match=palette,
        recommended_jewelry=jewelry,
        recommended_hairstyles=hairstyles,
        priority_looks=looks,
        message=message,
    )
    BRIDAL_LOGS.append({"customer_name": req.customer_name, "time": datetime.utcnow().isoformat()})
    return response


# ============================================================
# API ROUTES
# ============================================================

@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@app.get("/api/health", response_model=HealthResponse)
def api_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="Hi-Tech Beauty Salon Intelligence Dashboard",
        time=datetime.utcnow(),
    )


@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest) -> ChatResponse:
    return create_chat_reply(req)


@app.post("/api/consultation", response_model=ConsultationResponse)
def api_consultation(req: ConsultationRequest) -> ConsultationResponse:
    return build_consultation(req)


@app.post("/api/skin-analysis", response_model=SkinAnalysisResponse)
def api_skin_analysis(req: SkinAnalysisRequest) -> SkinAnalysisResponse:
    return analyze_skin(req)


@app.post("/api/hair-analysis", response_model=HairAnalysisResponse)
def api_hair_analysis(req: HairAnalysisRequest) -> HairAnalysisResponse:
    return analyze_hair(req)




@app.post("/api/foot-analysis")
def api_foot_analysis(payload: dict) -> JSONResponse:
    customer = payload.get("customer_name", "Guest")
    dryness = int(payload.get("dryness_score", 0))
    crack = int(payload.get("crack_score", 0))
    pain = int(payload.get("pain_score", 0))
    swelling = int(payload.get("swelling_score", 0))
    diabetic = bool(payload.get("diabetic_risk", False))
    index = round(100 - ((dryness + crack + pain + swelling) / 40) * 100, 1)
    issues=[]
    if dryness >= 5: issues.append("Heel dryness detected")
    if crack >= 5: issues.append("Crack risk detected")
    if pain >= 5: issues.append("Foot pain needs special care")
    if swelling >= 4: issues.append("Swelling should be monitored")
    if not issues: issues.append("No major foot issues detected")
    services=["Luxury pedicure", "Foot spa", "Heel repair ritual"]
    if diabetic: services.append("Diabetic-safe gentle foot care")
    homecare=["Use heel balm at night", "Avoid very hot water", "Keep feet dry between toes"]
    alerts=[]
    if diabetic: alerts.append("Medical caution: avoid aggressive scraping due to diabetic risk")
    summary = f"{customer} has a foot health index of {index}. Recommended next step is a salon-safe care plan with hydration and protective follow-up."
    return JSONResponse({
        "customer_name": customer,
        "foot_health_index": index,
        "detected_issues": issues,
        "salon_services": services,
        "homecare": homecare,
        "alerts": alerts,
        "ai_summary": summary
    })

@app.post("/api/bridal-analysis", response_model=BridalResponse)
def api_bridal_analysis(req: BridalRequest) -> BridalResponse:
    return analyze_bridal(req)


@app.get("/api/dashboard-metrics")
def api_dashboard_metrics() -> JSONResponse:
    return JSONResponse(
        {
            "live_chat_sessions": len(CHAT_LOGS),
            "consultations": len(CONSULT_LOGS),
            "skin_reports": len(SKIN_LOGS),
            "hair_reports": len(HAIR_LOGS),
            "bridal_reports": len(BRIDAL_LOGS),
        }
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Salon Intelligence Dashboard</title>
<style>
:root{
  --bg:#0b1020;
  --panel:#111827;
  --line:#273349;
  --text:#edf2ff;
  --muted:#9aa7bf;
  --accent:#d946ef;
  --accent2:#60a5fa;
  --gold:#f6c453;
  --radius:22px;
  --shadow:0 20px 50px rgba(0,0,0,.30);
}
*{box-sizing:border-box}
html,body{
  margin:0;padding:0;
  font-family:Inter,Segoe UI,Arial,sans-serif;
  background:linear-gradient(180deg,#090d18 0%,#0f172a 100%);
  color:var(--text);
}
body{min-height:100vh}
.container{
  display:grid;
  grid-template-columns:280px 1fr;
  min-height:100vh;
}
.sidebar{
  position:sticky;
  top:0;
  height:100vh;
  border-right:1px solid var(--line);
  background:rgba(8,12,20,.96);
  padding:22px 18px;
}
.brand{
  display:flex;
  gap:12px;
  align-items:center;
  margin-bottom:26px;
}
.logo{
  width:48px;height:48px;border-radius:16px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  box-shadow:var(--shadow);
}
.brand h1{margin:0;font-size:16px}
.brand p{margin:4px 0 0;color:var(--muted);font-size:12px}
.menu{
  display:flex;
  flex-direction:column;
  gap:8px;
}
.menu button{
  border:1px solid transparent;
  background:transparent;
  color:var(--text);
  padding:13px 14px;
  border-radius:14px;
  text-align:left;
  cursor:pointer;
  font-size:14px;
  transition:.2s;
}
.menu button:hover,.menu button.active{
  background:rgba(217,70,239,.08);
  border-color:rgba(217,70,239,.22);
}
.main{padding:28px}
.topbar{
  display:flex;
  justify-content:space-between;
  gap:18px;
  align-items:flex-start;
  margin-bottom:24px;
}
.title h2{margin:0;font-size:30px}
.title p{margin:8px 0 0;color:var(--muted);line-height:1.6}
.kpis{
  display:grid;
  grid-template-columns:repeat(5,1fr);
  gap:16px;
  margin-bottom:24px;
}
.kpi{
  border:1px solid var(--line);
  border-radius:18px;
  background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,.015));
  box-shadow:var(--shadow);
  padding:18px;
}
.kpi .label{font-size:12px;color:var(--muted)}
.kpi .value{font-size:28px;font-weight:800;margin-top:8px}
.kpi .sub{font-size:12px;color:#bfd0ee;margin-top:8px}
.services-card,.card{
  border:1px solid var(--line);
  border-radius:var(--radius);
  background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(255,255,255,.015));
  box-shadow:var(--shadow);
}
.card-head{
  padding:18px 20px;
  border-bottom:1px solid var(--line);
}
.card-head h3{margin:0;font-size:18px}
.card-head p{margin:6px 0 0;color:var(--muted);font-size:13px}
.card-body{padding:20px}
.services-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:12px;
}
.service-pill{
  border:1px solid var(--line);
  border-radius:16px;
  padding:14px;
  background:rgba(255,255,255,.025);
}
.service-pill strong{
  display:block;
  margin-bottom:6px;
  font-size:14px;
}
.service-pill span{
  color:var(--muted);
  font-size:12px;
  line-height:1.5;
}
.section{display:none}
.section.active{display:block}
.section-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:18px;
}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.field{display:flex;flex-direction:column;gap:8px;margin-bottom:14px}
label{font-size:13px;color:#dbe7ff}
input,select,textarea{
  width:100%;
  border:1px solid var(--line);
  background:#0c1320;
  color:var(--text);
  padding:13px 14px;
  border-radius:14px;
  font-size:14px;
  outline:none;
}
textarea{min-height:105px;resize:vertical}
.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px}
button.primary{
  background:linear-gradient(135deg,var(--accent),#a855f7);
  color:white;
  border:none;
  padding:12px 18px;
  border-radius:14px;
  font-weight:700;
  cursor:pointer;
}
button.secondary{
  background:#0c1320;
  color:white;
  border:1px solid var(--line);
  padding:12px 18px;
  border-radius:14px;
  cursor:pointer;
}
.output{
  border:1px solid var(--line);
  background:#0c1320;
  border-radius:16px;
  min-height:360px;
  padding:16px;
  overflow:auto;
}
.output h4{margin:0 0 12px;font-size:15px}
.output pre{
  margin:0;
  white-space:pre-wrap;
  word-break:break-word;
  font-size:13px;
  line-height:1.55;
  color:#dbe8ff;
  font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}

/* POPUP CHATBOT */
.chat-launcher{
  position:fixed;
  right:24px;
  bottom:24px;
  width:68px;
  height:68px;
  border:none;
  border-radius:999px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:white;
  font-size:26px;
  box-shadow:var(--shadow);
  cursor:pointer;
  z-index:1000;
}
.chat-popup{
  position:fixed;
  right:24px;
  bottom:100px;
  width:450px;
  max-width:calc(100vw - 24px);
  height:690px;
  max-height:86vh;
  display:none;
  flex-direction:column;
  border:1px solid var(--line);
  border-radius:24px;
  overflow:hidden;
  background:linear-gradient(180deg,#0d1320 0%, #131c2c 100%);
  box-shadow:var(--shadow);
  z-index:1001;
}
.chat-popup.open{display:flex}
.chat-top{
  padding:16px 18px;
  border-bottom:1px solid var(--line);
  display:flex;
  justify-content:space-between;
  align-items:center;
  background:rgba(255,255,255,.03);
}
.chat-top h3{margin:0;font-size:16px}
.chat-top span{font-size:12px;color:var(--muted)}
.chat-close{
  border:none;background:transparent;color:white;font-size:22px;cursor:pointer
}
.bot-stage{
  border-bottom:1px solid var(--line);
  background:
    radial-gradient(circle at 18% 22%, rgba(96,165,250,.18), transparent 18%),
    radial-gradient(circle at 82% 18%, rgba(217,70,239,.20), transparent 18%),
    radial-gradient(circle at 50% 50%, rgba(246,196,83,.08), transparent 35%),
    linear-gradient(180deg,#121b2d 0%, #101828 100%);
  padding:12px 14px;
  position:relative;
}
.bot-shell{
  display:grid;
  grid-template-columns:170px 1fr;
  gap:16px;
  align-items:center;
}
.bot-svg-wrap{
  display:flex;
  justify-content:center;
  align-items:center;
}
.bot-svg{
  width:152px;
  height:152px;
  filter: drop-shadow(0 12px 20px rgba(0,0,0,.25));
  animation:botFloat 3.8s ease-in-out infinite;
}
.bot-arm-wave{
  animation:botWave 2.5s ease-in-out infinite;
  transform-origin:126px 92px;
}
.bot-eye{
  animation:botBlink 5s infinite;
  transform-origin:center;
}
.sparkle{
  position:absolute;
  width:8px;
  height:8px;
  border-radius:50%;
  background:radial-gradient(circle,#fff8c7 0%, #ffd86b 45%, rgba(255,216,107,0) 80%);
  box-shadow:0 0 10px rgba(255,216,107,.75);
  animation:twinkle 1.9s infinite ease-in-out;
}
.sparkle.s1{top:22px;left:24px;animation-delay:.1s}
.sparkle.s2{top:34px;right:40px;animation-delay:.6s}
.sparkle.s3{bottom:28px;left:64px;animation-delay:1.1s}
.sparkle.s4{top:62px;right:120px;animation-delay:1.5s}
.sparkle.s5{bottom:46px;right:56px;animation-delay:.9s}
.bot-info strong{
  display:block;
  font-size:17px;
  margin-bottom:4px;
}
.bot-role{
  display:block;
  color:#f9c5ff;
  font-size:12px;
  margin-bottom:8px;
}
.bot-info p{
  margin:0;
  color:var(--muted);
  font-size:12px;
  line-height:1.55;
}
.bot-calendar-btn{
  margin-top:10px;
  border:none;
  border-radius:12px;
  padding:10px 12px;
  color:white;
  cursor:pointer;
  font-size:12px;
  font-weight:700;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
}
.chat-body{
  flex:1;
  overflow:auto;
  padding:14px;
  display:flex;
  flex-direction:column;
  gap:10px;
}
.msg{
  max-width:85%;
  padding:12px 14px;
  border-radius:16px;
  font-size:13px;
  line-height:1.5;
  white-space:pre-wrap;
}
.msg.bot{
  align-self:flex-start;
  background:rgba(255,255,255,.06);
  border:1px solid var(--line);
}
.msg.user{
  align-self:flex-end;
  background:linear-gradient(135deg,var(--accent),#a855f7);
  color:white;
}
.msg.typing{
  display:flex;
  align-items:center;
  gap:6px;
}
.typing-dots{
  display:inline-flex;
  gap:5px;
  align-items:center;
}
.typing-dots span{
  width:8px;
  height:8px;
  border-radius:50%;
  background:#c084fc;
  animation:typingBounce 1s infinite ease-in-out;
}
.typing-dots span:nth-child(2){animation-delay:.16s}
.typing-dots span:nth-child(3){animation-delay:.32s}
.chat-controls{
  padding:12px 14px;
  border-top:1px solid var(--line);
  display:grid;
  grid-template-columns:1fr 108px;
  gap:10px;
}
.chat-controls input,
.chat-controls select{
  padding:12px;
  border-radius:12px;
}
.chat-row{
  display:grid;
  grid-template-columns:1fr 110px;
  gap:10px;
  padding:0 14px 12px;
}
.chat-send{
  border:none;
  border-radius:12px;
  background:linear-gradient(135deg,var(--accent),#a855f7);
  color:white;
  font-weight:700;
  cursor:pointer;
}
.chat-mini-note{
  padding:0 14px 10px;
  font-size:11px;
  color:var(--muted);
}
.calendar-modal{
  position:fixed;
  inset:0;
  background:rgba(7,10,18,.68);
  display:none;
  align-items:center;
  justify-content:center;
  padding:18px;
  z-index:1002;
}
.calendar-modal.open{display:flex}
.calendar-card{
  width:min(420px,100%);
  border:1px solid var(--line);
  border-radius:24px;
  overflow:hidden;
  background:linear-gradient(180deg,#101826 0%, #182235 100%);
  box-shadow:var(--shadow);
  transform:perspective(900px) rotateX(10deg) rotateY(-11deg);
}
.calendar-head{
  padding:16px 18px;
  background:linear-gradient(135deg,var(--accent),var(--accent2));
  color:white;
}
.calendar-head h4{margin:0;font-size:20px}
.calendar-head p{margin:6px 0 0;font-size:12px;opacity:.9}
.calendar-grid{
  padding:16px;
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:12px;
}
.slot{
  border:1px solid var(--line);
  border-radius:16px;
  padding:14px;
  background:rgba(255,255,255,.04);
}
.slot strong{display:block;margin-bottom:6px}
.slot span{font-size:12px;color:#c9d7f0}
.calendar-close{
  position:absolute;
  margin:14px;
  right:0;
  top:0;
  border:none;
  background:rgba(255,255,255,.12);
  color:white;
  width:38px;
  height:38px;
  border-radius:999px;
  cursor:pointer;
}

@keyframes botFloat{
  0%,100%{transform:translateY(0)}
  50%{transform:translateY(-5px)}
}
@keyframes botWave{
  0%,100%{transform:rotate(0deg)}
  20%{transform:rotate(-8deg)}
  45%{transform:rotate(14deg)}
  65%{transform:rotate(-5deg)}
}
@keyframes botBlink{
  0%,48%,52%,100%{transform:scaleY(1)}
  50%{transform:scaleY(0.12)}
}
@keyframes typingBounce{
  0%,80%,100%{transform:translateY(0);opacity:.45}
  40%{transform:translateY(-4px);opacity:1}
}
@keyframes twinkle{
  0%,100%{transform:scale(.6);opacity:.45}
  50%{transform:scale(1.2);opacity:1}
}

@media (max-width: 1180px){
  .kpis{grid-template-columns:repeat(2,1fr)}
  .section-grid{grid-template-columns:1fr}
}
@media (max-width: 820px){
  .container{grid-template-columns:1fr}
  .sidebar{position:relative;height:auto;border-right:none;border-bottom:1px solid var(--line)}
  .grid-2,.grid-3,.services-grid{grid-template-columns:1fr}
  .chat-popup{right:12px;bottom:84px;width:calc(100vw - 24px)}
  .chat-launcher{right:12px;bottom:12px}
  .bot-shell{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="container">
  <aside class="sidebar">
    <div class="brand">
      <div class="logo"></div>
      <div>
        <h1>Salon Intelligence</h1>
        <p>Beauty salon experience dashboard</p>
      </div>
    </div>

    <div class="menu">
      <button class="active" onclick="showSection('home', this)">Home</button>
      <button onclick="showSection('consult', this)">Consultation Scan</button>
      <button onclick="showSection('skin', this)">Skin Report</button>
      <button onclick="showSection('hair', this)">Hair Report</button>
      <button onclick="showSection('bridal', this)">Bridal Stylist</button>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div class="title">
        <h2>Luxury Beauty Salon Dashboard</h2>
        <p>Professional customer experience, salon intelligence, and beauty recommendation workflows from one elegant interface.</p>
      </div>
    </div>

    <div class="kpis">
      <div class="kpi"><div class="label">Chat Sessions</div><div id="kpiChats" class="value">0</div><div class="sub">Customer conversations</div></div>
      <div class="kpi"><div class="label">Consultations</div><div id="kpiConsult" class="value">0</div><div class="sub">Service scans</div></div>
      <div class="kpi"><div class="label">Skin Reports</div><div id="kpiSkin" class="value">0</div><div class="sub">Facial insights</div></div>
      <div class="kpi"><div class="label">Hair Reports</div><div id="kpiHair" class="value">0</div><div class="sub">Treatment & color insights</div></div>
      <div class="kpi"><div class="label">Bridal Reports</div><div id="kpiBridal" class="value">0</div><div class="sub">Styling looks</div></div>
    </div>

    <section id="home" class="section active">
      <div class="services-card">
        <div class="card-head">
          <h3>Signature Services</h3>
          <p>Premium salon experiences for skin, hair, nails, bridal styling, and hair coloring.</p>
        </div>
        <div class="card-body">
          <div class="services-grid">
            <div class="service-pill">
              <strong>Facials</strong>
              <span>Glow, hydration, acne-control, tan removal, and sensitive-skin care.</span>
            </div>
            <div class="service-pill">
              <strong>Hair Studio</strong>
              <span>Haircut suggestions, hair spa, scalp therapy, dandruff and hair fall care, plus global color, root touch-up, balayage, ombré, gloss, toner, and color-safe aftercare.</span>
            </div>
            <div class="service-pill">
              <strong>Hair Color Bar</strong>
              <span>Chocolate brown, balayage, highlights, burgundy, mocha tones, root touch-up, global coloring, gloss finish, brass neutralizing toner, and color-protection care.</span>
            </div>
            <div class="service-pill">
              <strong>Nails & Foot Care</strong>
              <span>Manicure, pedicure, reflexology, and premium relaxation services.</span>
            </div>
            <div class="service-pill">
              <strong>Bridal Lounge</strong>
              <span>Bridal makeup, skin prep, saree styling, and premium finishing care.</span>
            </div>
            <div class="service-pill">
              <strong>Bot-tique Assistant</strong>
              <span>Rybo is a cheerful cute robot assistant for quick FAQs, appointment guidance, service suggestions, and animated salon support.</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section id="consult" class="section">
      <div class="section-grid">
        <div class="card">
          <div class="card-head">
            <h3>Consultation Scan</h3>
            <p>Generate personalised service recommendations from observed client profile inputs.</p>
          </div>
          <div class="card-body">
            <div class="grid-2">
              <div class="field"><label>Customer name</label><input id="con_name" value="Karthi" /></div>
              <div class="field">
                <label>Language</label>
                <select id="con_language">
                  <option value="english">English</option>
                  <option value="tamil">Tamil</option>
                </select>
              </div>
            </div>

            <div class="grid-2">
              <div class="field">
                <label>Face shape</label>
                <select id="con_face_shape">
                  <option value="round">Round</option>
                  <option value="oval">Oval</option>
                  <option value="square">Square</option>
                  <option value="heart">Heart</option>
                  <option value="diamond">Diamond</option>
                  <option value="oblong">Oblong</option>
                </select>
              </div>
              <div class="field">
                <label>Skin type</label>
                <select id="con_skin_type">
                  <option value="oily">Oily</option>
                  <option value="dry">Dry</option>
                  <option value="combination">Combination</option>
                  <option value="sensitive">Sensitive</option>
                  <option value="normal">Normal</option>
                  <option value="acne_prone">Acne Prone</option>
                </select>
              </div>
            </div>

            <div class="grid-2">
              <div class="field">
                <label>Hair type</label>
                <select id="con_hair_type">
                  <option value="wavy">Wavy</option>
                  <option value="straight">Straight</option>
                  <option value="curly">Curly</option>
                  <option value="coily">Coily</option>
                </select>
              </div>
              <div class="field">
                <label>Hair condition</label>
                <select id="con_hair_condition">
                  <option value="hair_fall">Hair Fall</option>
                  <option value="frizzy">Frizzy</option>
                  <option value="damaged">Damaged</option>
                  <option value="dry">Dry</option>
                  <option value="dandruff">Dandruff</option>
                  <option value="thinning">Thinning</option>
                  <option value="healthy">Healthy</option>
                </select>
              </div>
            </div>

            <div class="grid-2">
              <div class="field">
                <label>Concern</label>
                <input id="con_concern" value="Need haircut, facial and hair color suggestion" />
              </div>
              <div class="field">
                <label>Budget (INR)</label>
                <input id="con_budget" type="number" value="15000" />
              </div>
            </div>

            <div class="field">
              <label>Bridal interest</label>
              <select id="con_bridal_interest">
                <option value="false">No</option>
                <option value="true">Yes</option>
              </select>
            </div>

            <div class="actions">
              <button class="primary" onclick="runConsultation()">Generate report</button>
              <button class="secondary" onclick="fillConsultDemo()">Load demo</button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-head">
            <h3>Consultation Report</h3>
            <p>Haircut, facial, hair color, premium add-ons, and warnings.</p>
          </div>
          <div class="card-body">
            <div id="consult_output" class="output"><h4>Report</h4><pre>Waiting for test...</pre></div>
          </div>
        </div>
      </div>
    </section>

    <section id="skin" class="section">
      <div class="section-grid">
        <div class="card">
          <div class="card-head">
            <h3>Skin Report</h3>
            <p>Create facial recommendation reports from client skin profile.</p>
          </div>
          <div class="card-body">
            <div class="grid-2">
              <div class="field"><label>Customer name</label><input id="skin_name" value="Anita" /></div>
              <div class="field">
                <label>Skin type</label>
                <select id="skin_type">
                  <option value="sensitive">Sensitive</option>
                  <option value="oily">Oily</option>
                  <option value="dry">Dry</option>
                  <option value="combination">Combination</option>
                  <option value="normal">Normal</option>
                  <option value="acne_prone">Acne Prone</option>
                </select>
              </div>
            </div>

            <div class="grid-3">
              <div class="field"><label>Acne</label><input id="skin_acne" type="number" min="0" max="10" value="3" /></div>
              <div class="field"><label>Pigmentation</label><input id="skin_pigment" type="number" min="0" max="10" value="6" /></div>
              <div class="field"><label>Dryness</label><input id="skin_dryness" type="number" min="0" max="10" value="5" /></div>
            </div>

            <div class="grid-2">
              <div class="field"><label>Sensitivity</label><input id="skin_sensitivity" type="number" min="0" max="10" value="8" /></div>
              <div class="field"><label>Tanning</label><input id="skin_tanning" type="number" min="0" max="10" value="4" /></div>
            </div>

            <div class="actions">
              <button class="primary" onclick="runSkin()">Generate skin report</button>
              <button class="secondary" onclick="fillSkinDemo()">Load demo</button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-head">
            <h3>Skin Output</h3>
            <p>Facials, warnings, and homecare guidance.</p>
          </div>
          <div class="card-body">
            <div id="skin_output" class="output"><h4>Skin Report</h4><pre>Waiting for test...</pre></div>
          </div>
        </div>
      </div>
    </section>

    <section id="hair" class="section">
      <div class="section-grid">
        <div class="card">
          <div class="card-head">
            <h3>Hair Report</h3>
            <p>Create treatment, hairstyle, haircut, and hair color recommendations.</p>
          </div>
          <div class="card-body">
            <div class="grid-2">
              <div class="field"><label>Customer name</label><input id="hair_name" value="Kaviya" /></div>
              <div class="field">
                <label>Face shape</label>
                <select id="hair_face_shape">
                  <option value="round">Round</option>
                  <option value="oval">Oval</option>
                  <option value="square">Square</option>
                  <option value="heart">Heart</option>
                  <option value="diamond">Diamond</option>
                  <option value="oblong">Oblong</option>
                </select>
              </div>
            </div>

            <div class="grid-2">
              <div class="field">
                <label>Hair type</label>
                <select id="hair_type">
                  <option value="curly">Curly</option>
                  <option value="wavy">Wavy</option>
                  <option value="straight">Straight</option>
                  <option value="coily">Coily</option>
                </select>
              </div>
              <div class="field">
                <label>Hair condition</label>
                <select id="hair_condition">
                  <option value="frizzy">Frizzy</option>
                  <option value="hair_fall">Hair Fall</option>
                  <option value="damaged">Damaged</option>
                  <option value="dry">Dry</option>
                  <option value="dandruff">Dandruff</option>
                  <option value="thinning">Thinning</option>
                  <option value="healthy">Healthy</option>
                </select>
              </div>
            </div>

            <div class="grid-2">
              <div class="field"><label>Dandruff</label><input id="hair_dandruff" type="number" min="0" max="10" value="3" /></div>
              <div class="field"><label>Hair Fall</label><input id="hair_fall" type="number" min="0" max="10" value="6" /></div>
            </div>

            <div class="grid-2">
              <div class="field"><label>Breakage</label><input id="hair_breakage" type="number" min="0" max="10" value="7" /></div>
              <div class="field"><label>Scalp Oiliness</label><input id="hair_oiliness" type="number" min="0" max="10" value="4" /></div>
            </div>

            <div class="field">
              <label>Chemical history</label>
              <select id="hair_chemical_history">
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>

            <div class="actions">
              <button class="primary" onclick="runHair()">Generate hair report</button>
              <button class="secondary" onclick="fillHairDemo()">Load demo</button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-head">
            <h3>Hair Output</h3>
            <p>Treatment plan, hairstyle fit, color match, and aftercare guidance.</p>
          </div>
          <div class="card-body">
            <div id="hair_output" class="output"><h4>Hair Report</h4><pre>Waiting for test...</pre></div>
          </div>
        </div>
      </div>
    </section>

    <section id="bridal" class="section">
      <div class="section-grid">
        <div class="card">
          <div class="card-head">
            <h3>Bridal Stylist</h3>
            <p>Create bridal palette and look suggestions.</p>
          </div>
          <div class="card-body">
            <div class="grid-2">
              <div class="field"><label>Customer name</label><input id="bridal_name" value="Meena" /></div>
              <div class="field"><label>Saree color</label><input id="bridal_color" value="red" /></div>
            </div>

            <div class="grid-2">
              <div class="field"><label>Saree fabric</label><input id="bridal_fabric" value="kanjeevaram silk" /></div>
              <div class="field"><label>Saree pattern</label><input id="bridal_pattern" value="zari floral" /></div>
            </div>

            <div class="field">
              <label>Modern touch</label>
              <select id="bridal_modern">
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>

            <div class="actions">
              <button class="primary" onclick="runBridal()">Generate bridal report</button>
              <button class="secondary" onclick="fillBridalDemo()">Load demo</button>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-head">
            <h3>Bridal Output</h3>
            <p>Palette, jewelry, hairstyle, and priority looks.</p>
          </div>
          <div class="card-body">
            <div id="bridal_output" class="output"><h4>Bridal Report</h4><pre>Waiting for test...</pre></div>
          </div>
        </div>
      </div>
    </section>
  </main>
</div>


<button class="chat-launcher" onclick="toggleChatbot()">🤖</button>

<div id="chatPopup" class="chat-popup">
  <div class="chat-top">
    <div>
      <h3>Rybo</h3>
      <span>The Friendly “Bot-tique” Assistant</span>
    </div>
    <button class="chat-close" onclick="toggleChatbot()">×</button>
  </div>

  <div class="bot-stage">
    <div class="sparkle s1"></div>
    <div class="sparkle s2"></div>
    <div class="sparkle s3"></div>
    <div class="sparkle s4"></div>
    <div class="sparkle s5"></div>

    <div class="bot-shell">
      <div class="bot-svg-wrap">
        <svg class="bot-svg" viewBox="0 0 170 170" xmlns="http://www.w3.org/2000/svg" aria-label="Rybo cute salon assistant robot">
          <defs>
            <linearGradient id="botHead" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#fde7f3"/>
              <stop offset="55%" stop-color="#e9ddff"/>
              <stop offset="100%" stop-color="#d8f8ff"/>
            </linearGradient>
            <linearGradient id="botBody" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#d946ef"/>
              <stop offset="55%" stop-color="#8b5cf6"/>
              <stop offset="100%" stop-color="#60a5fa"/>
            </linearGradient>
          </defs>
          <ellipse cx="84" cy="154" rx="42" ry="8" fill="rgba(0,0,0,.16)"/>
          <line x1="84" y1="16" x2="84" y2="30" stroke="#8b5cf6" stroke-width="5" stroke-linecap="round"/>
          <circle cx="84" cy="11" r="8" fill="#d946ef"/>
          <rect x="35" y="30" width="98" height="74" rx="24" fill="url(#botHead)" stroke="#c084fc" stroke-width="3"/>
          <rect x="52" y="49" width="64" height="32" rx="14" fill="#172033" opacity=".96"/>
          <ellipse class="bot-eye" cx="70" cy="65" rx="7" ry="9" fill="#67e8f9"/>
          <ellipse class="bot-eye" cx="98" cy="65" rx="7" ry="9" fill="#f9a8d4"/>
          <circle cx="70" cy="64" r="2.6" fill="white"/>
          <circle cx="98" cy="64" r="2.6" fill="white"/>
          <path d="M69 86 Q84 97 99 86" fill="none" stroke="#8b5cf6" stroke-width="4" stroke-linecap="round"/>
          <rect x="51" y="108" width="66" height="40" rx="18" fill="url(#botBody)"/>
          <circle cx="72" cy="128" r="5.5" fill="rgba(255,255,255,.9)"/>
          <circle cx="84" cy="128" r="5.5" fill="rgba(255,255,255,.9)"/>
          <circle cx="96" cy="128" r="5.5" fill="rgba(255,255,255,.9)"/>
          <line x1="51" y1="120" x2="26" y2="101" stroke="#60a5fa" stroke-width="9" stroke-linecap="round"/>
          <circle cx="21" cy="97" r="10" fill="#d8f8ff" stroke="#67e8f9" stroke-width="3"/>
          <g class="bot-arm-wave">
            <line x1="117" y1="120" x2="142" y2="98" stroke="#8b5cf6" stroke-width="9" stroke-linecap="round"/>
            <circle cx="147" cy="94" r="10" fill="#fde7f3" stroke="#c084fc" stroke-width="3"/>
          </g>
          <line x1="67" y1="147" x2="56" y2="163" stroke="#8b5cf6" stroke-width="8" stroke-linecap="round"/>
          <line x1="101" y1="147" x2="112" y2="163" stroke="#60a5fa" stroke-width="8" stroke-linecap="round"/>
        </svg>
      </div>

      <div class="bot-info">
        <strong>Rybo</strong>
        <span class="bot-role">Friendly Bot-tique Assistant • Cute Robot</span>
        <p>
          Cheerful, efficient, and tech-savvy salon helper for quick FAQs, bookings,
          hair color guidance, bridal support, and fast front-desk assistance.
        </p>
        <button class="bot-calendar-btn" onclick="openCalendarModal()">Show 3D Calendar</button>
      </div>
    </div>
  </div>

  <div id="chatBody" class="chat-body"></div>

  <div class="chat-row">
    <select id="popup_lang">
      <option value="tamil">Tamil</option>
      <option value="english">English</option>
    </select>
    <input id="popup_name" placeholder="Your name" value="Guest" />
  </div>

  <div class="chat-controls">
    <input id="popup_message" placeholder="Ask about facial, haircut, hair color, bridal..." />
    <button class="chat-send" onclick="sendPopupMessage()">Send</button>
  </div>
  <div class="chat-mini-note">
    Example: “எனக்கு facial details வேண்டும்”, “I need haircut and hair color”, “Do you have bridal package?”
  </div>
</div>

<div id="calendarModal" class="calendar-modal" onclick="closeCalendarBackdrop(event)">
  <div class="calendar-card">
    <button class="calendar-close" onclick="closeCalendarModal()">×</button>
    <div class="calendar-head">
      <h4>Rybo’s 3D Calendar</h4>
      <p>Quick appointment slot preview for modern salons</p>
    </div>
    <div class="calendar-grid">
      <div class="slot"><strong>5:30 PM</strong><span>Hair color consultation</span></div>
      <div class="slot"><strong>6:15 PM</strong><span>Root touch-up</span></div>
      <div class="slot"><strong>7:00 PM</strong><span>Hair spa and styling</span></div>
      <div class="slot"><strong>7:45 PM</strong><span>Bridal trial slot</span></div>
    </div>
  </div>
</div>

<script>
function showSection(id, btn){
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.menu button').forEach(b => b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  if (btn) btn.classList.add('active');
}

function pretty(obj){
  return JSON.stringify(obj, null, 2);
}

async function postJSON(url, payload){
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  if (!res.ok){
    throw new Error(await res.text());
  }
  return await res.json();
}

async function refreshMetrics(){
  try{
    const res = await fetch('/api/dashboard-metrics');
    const data = await res.json();
    document.getElementById('kpiChats').textContent = data.live_chat_sessions;
    document.getElementById('kpiConsult').textContent = data.consultations;
    document.getElementById('kpiSkin').textContent = data.skin_reports;
    document.getElementById('kpiHair').textContent = data.hair_reports;
    document.getElementById('kpiBridal').textContent = data.bridal_reports;
  } catch(e) {}
}

function fillConsultDemo(){
  document.getElementById('con_name').value = 'Karthi';
  document.getElementById('con_language').value = 'english';
  document.getElementById('con_face_shape').value = 'round';
  document.getElementById('con_skin_type').value = 'oily';
  document.getElementById('con_hair_type').value = 'wavy';
  document.getElementById('con_hair_condition').value = 'hair_fall';
  document.getElementById('con_concern').value = 'Need haircut, facial and hair color suggestion';
  document.getElementById('con_budget').value = '15000';
  document.getElementById('con_bridal_interest').value = 'false';
}

async function runConsultation(){
  const payload = {
    customer_name: document.getElementById('con_name').value,
    language: document.getElementById('con_language').value,
    face_shape: document.getElementById('con_face_shape').value,
    skin_type: document.getElementById('con_skin_type').value,
    hair_type: document.getElementById('con_hair_type').value,
    hair_condition: document.getElementById('con_hair_condition').value,
    bridal_interest: document.getElementById('con_bridal_interest').value === 'true',
    concern: document.getElementById('con_concern').value,
    budget_inr: Number(document.getElementById('con_budget').value || 0)
  };
  const out = document.getElementById('consult_output');
  out.innerHTML = '<h4>Report</h4><pre>Loading...</pre>';
  try{
    const data = await postJSON('/api/consultation', payload);
    out.innerHTML = '<h4>Report</h4><pre>' + pretty(data) + '</pre>';
    refreshMetrics();
  } catch(e){
    out.innerHTML = '<h4>Error</h4><pre>' + e.message + '</pre>';
  }
}

function fillSkinDemo(){
  document.getElementById('skin_name').value = 'Anita';
  document.getElementById('skin_type').value = 'sensitive';
  document.getElementById('skin_acne').value = '3';
  document.getElementById('skin_pigment').value = '6';
  document.getElementById('skin_dryness').value = '5';
  document.getElementById('skin_sensitivity').value = '8';
  document.getElementById('skin_tanning').value = '4';
}

async function runSkin(){
  const payload = {
    customer_name: document.getElementById('skin_name').value,
    skin_type: document.getElementById('skin_type').value,
    acne_score: Number(document.getElementById('skin_acne').value),
    pigmentation_score: Number(document.getElementById('skin_pigment').value),
    dryness_score: Number(document.getElementById('skin_dryness').value),
    sensitivity_score: Number(document.getElementById('skin_sensitivity').value),
    tanning_score: Number(document.getElementById('skin_tanning').value)
  };
  const out = document.getElementById('skin_output');
  out.innerHTML = '<h4>Skin Report</h4><pre>Loading...</pre>';
  try{
    const data = await postJSON('/api/skin-analysis', payload);
    out.innerHTML = '<h4>Skin Report</h4><pre>' + pretty(data) + '</pre>';
    refreshMetrics();
  } catch(e){
    out.innerHTML = '<h4>Error</h4><pre>' + e.message + '</pre>';
  }
}

function fillHairDemo(){
  document.getElementById('hair_name').value = 'Kaviya';
  document.getElementById('hair_face_shape').value = 'round';
  document.getElementById('hair_type').value = 'curly';
  document.getElementById('hair_condition').value = 'frizzy';
  document.getElementById('hair_dandruff').value = '3';
  document.getElementById('hair_fall').value = '6';
  document.getElementById('hair_breakage').value = '7';
  document.getElementById('hair_oiliness').value = '4';
  document.getElementById('hair_chemical_history').value = 'true';
}

async function runHair(){
  const payload = {
    customer_name: document.getElementById('hair_name').value,
    face_shape: document.getElementById('hair_face_shape').value,
    hair_type: document.getElementById('hair_type').value,
    hair_condition: document.getElementById('hair_condition').value,
    dandruff_score: Number(document.getElementById('hair_dandruff').value),
    hair_fall_score: Number(document.getElementById('hair_fall').value),
    breakage_score: Number(document.getElementById('hair_breakage').value),
    scalp_oiliness: Number(document.getElementById('hair_oiliness').value),
    chemical_history: document.getElementById('hair_chemical_history').value === 'true'
  };
  const out = document.getElementById('hair_output');
  out.innerHTML = '<h4>Hair Report</h4><pre>Loading...</pre>';
  try{
    const data = await postJSON('/api/hair-analysis', payload);
    out.innerHTML = '<h4>Hair Report</h4><pre>' + pretty(data) + '</pre>';
    refreshMetrics();
  } catch(e){
    out.innerHTML = '<h4>Error</h4><pre>' + e.message + '</pre>';
  }
}

function fillBridalDemo(){
  document.getElementById('bridal_name').value = 'Meena';
  document.getElementById('bridal_color').value = 'red';
  document.getElementById('bridal_fabric').value = 'kanjeevaram silk';
  document.getElementById('bridal_pattern').value = 'zari floral';
  document.getElementById('bridal_modern').value = 'true';
}

async function runBridal(){
  const payload = {
    customer_name: document.getElementById('bridal_name').value,
    saree_color: document.getElementById('bridal_color').value,
    saree_fabric: document.getElementById('bridal_fabric').value,
    saree_pattern: document.getElementById('bridal_pattern').value,
    wants_modern_touch: document.getElementById('bridal_modern').value === 'true'
  };
  const out = document.getElementById('bridal_output');
  out.innerHTML = '<h4>Bridal Report</h4><pre>Loading...</pre>';
  try{
    const data = await postJSON('/api/bridal-analysis', payload);
    out.innerHTML = '<h4>Bridal Report</h4><pre>' + pretty(data) + '</pre>';
    refreshMetrics();
  } catch(e){
    out.innerHTML = '<h4>Error</h4><pre>' + e.message + '</pre>';
  }
}


function toggleChatbot(){
  const popup = document.getElementById('chatPopup');
  popup.classList.toggle('open');
  if (popup.classList.contains('open') && document.getElementById('chatBody').children.length === 0){
    welcomeChat();
  }
}

function addChatMessage(role, text, htmlContent=null){
  const box = document.getElementById('chatBody');
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  if (htmlContent){
    div.innerHTML = htmlContent;
  } else {
    div.textContent = text;
  }
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div;
}

function welcomeChat(){
  const name = document.getElementById('popup_name').value || 'Guest';
  const greeting = `வணக்கம் ${name}. நான் Rybo, உங்கள் friendly Bot-tique assistant. Facial, haircut, hair color, bridal, manicure, pedicure, hair spa மற்றும் quick booking support பற்றி கேட்கலாம்.`;
  addChatMessage('bot', greeting);
}

function openCalendarModal(){
  document.getElementById('calendarModal').classList.add('open');
}

function closeCalendarModal(){
  document.getElementById('calendarModal').classList.remove('open');
}

function closeCalendarBackdrop(event){
  if (event.target.id === 'calendarModal'){
    closeCalendarModal();
  }
}

async function sendPopupMessage(){
  const input = document.getElementById('popup_message');
  const name = document.getElementById('popup_name').value || 'Guest';
  const lang = document.getElementById('popup_lang').value;
  const text = input.value.trim();

  if (!text) return;

  addChatMessage('user', text);
  input.value = '';

  const typingEl = addChatMessage(
    'bot typing',
    '',
    'Rybo is typing <span class="typing-dots"><span></span><span></span><span></span></span>'
  );

  try{
    const data = await postJSON('/api/chat', {
      customer_name: name,
      language: lang,
      message: text,
      context: 'popup chatbot'
    });

    typingEl.remove();

    let botReply = data.reply;
    if (data.suggested_services && data.suggested_services.length){
      botReply += "\n\nSuggested services: " + data.suggested_services.join(", ");
    }
    if (data.next_step){
      botReply += "\nNext step: " + data.next_step;
    }

    addChatMessage('bot', botReply);
    refreshMetrics();
  } catch(e){
    typingEl.remove();
    addChatMessage('bot', 'Error: ' + e.message);
  }
}

document.addEventListener('DOMContentLoaded', function(){
  const input = document.getElementById('popup_message');
  input.addEventListener('keydown', function(e){
    if (e.key === 'Enter'){
      e.preventDefault();
      sendPopupMessage();
    }
  });
  refreshMetrics();
});
</script>
</body>
</html>
"""
    return HTMLResponse(content=html)