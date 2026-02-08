# astro_engine.py — Vedic Astrology Calculation Engine
# Uses pyswisseph (Swiss Ephemeris) when available for accurate planetary positions.
# Falls back to a lightweight mean-motion ephemeris when pyswisseph is unavailable.

from datetime import datetime, date, time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

try:
    import swisseph as swe
    SWE_AVAILABLE = True
except Exception:
    swe = None
    SWE_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

if SWE_AVAILABLE:
    # Initialize Swiss Ephemeris with Lahiri ayanamsa (Vedic/Sidereal)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    PLANET_IDS = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,  # North Node (Mean)
    }
else:
    PLANET_IDS = {}

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Zodiac signs in order
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Sign rulers (Vedic)
SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Elements
SIGN_ELEMENTS = {
    "Aries": "Fire", "Taurus": "Earth", "Gemini": "Air", "Cancer": "Water",
    "Leo": "Fire", "Virgo": "Earth", "Libra": "Air", "Scorpio": "Water",
    "Sagittarius": "Fire", "Capricorn": "Earth", "Aquarius": "Air", "Pisces": "Water"
}

# 27 Nakshatras with their lords
NAKSHATRAS = [
    ("Ashwini", "Ketu"), ("Bharani", "Venus"), ("Krittika", "Sun"),
    ("Rohini", "Moon"), ("Mrigashira", "Mars"), ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"), ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"), ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"), ("Chitra", "Mars"), ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"), ("Anuradha", "Saturn"), ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"), ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"), ("Dhanishta", "Mars"), ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]

# Vimshottari Dasha periods (years)
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
    "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]

# Mean longitudes (deg) at J2000 and mean daily motion (deg/day)
MEAN_LONGITUDE = {
    "Sun": (280.46646, 0.98564736),
    "Moon": (218.316, 13.176396),
    "Mercury": (252.251, 4.09233445),
    "Venus": (181.979, 1.60213034),
    "Mars": (355.433, 0.52402068),
    "Jupiter": (34.351, 0.08308529),
    "Saturn": (50.077, 0.03344414),
    "Rahu": (125.04452, -0.0529538083),
}

# Synodic periods (days) for retrograde approximation
SYNODIC_PERIODS = {
    "Mercury": (116, 22),
    "Venus": (584, 42),
    "Mars": (780, 72),
    "Jupiter": (399, 121),
    "Saturn": (378, 140),
}


# ═══════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════

@dataclass
class PlanetPosition:
    planet: str
    longitude: float       # Sidereal longitude (0-360)
    sign: str              # Which zodiac sign
    sign_degree: float     # Degree within the sign (0-30)
    nakshatra: str         # Which nakshatra
    nakshatra_pada: int    # Which pada (1-4)
    is_retrograde: bool
    house: Optional[int] = None  # House number (1-12) if ascendant known


@dataclass
class TransitInfo:
    planet: str
    sign: str
    house_from_moon: int   # House from natal Moon sign
    is_retrograde: bool
    is_combust: bool       # Too close to Sun
    aspect_info: str       # Key aspects being formed


@dataclass
class CosmicBattery:
    percentage: int        # 0-100
    level: str             # "peak", "good", "neutral", "low", "critical"
    factors: List[str]     # What's contributing to the score
    message: str


# ═══════════════════════════════════════════════════════════════
# CORE CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════


def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day number."""
    if SWE_AVAILABLE:
        return swe.julday(
            dt.year, dt.month, dt.day,
            dt.hour + dt.minute / 60.0 + dt.second / 3600.0
        )

    # Fallback Julian Day calculation
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0

    if month <= 2:
        year -= 1
        month += 12

    a = year // 100
    b = 2 - a + (a // 4)
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b - 1524.5
    return jd + (hour / 24.0)


def get_ayanamsa(jd: float) -> float:
    """Get the Lahiri ayanamsa value for a given Julian Day."""
    if SWE_AVAILABLE:
        return swe.get_ayanamsa(jd)

    # Approximate Lahiri ayanamsa (deg) using linear precession from J2000
    years_since_2000 = (jd - 2451545.0) / 365.25
    return 24.0 + 0.0139696 * years_since_2000


def _approx_retrograde(planet: str, d: float) -> bool:
    if planet in ("Rahu", "Ketu"):
        return True
    period = SYNODIC_PERIODS.get(planet)
    if not period:
        return False
    cycle, retro_window = period
    return (d % cycle) < retro_window


def get_sidereal_position(planet_name: str, jd: float) -> Tuple[float, bool]:
    """
    Calculate sidereal longitude of a planet.
    Returns (longitude, is_retrograde).
    """
    if SWE_AVAILABLE:
        planet_id = PLANET_IDS.get(planet_name)
        if planet_id is None:
            raise ValueError(f"Unknown planet: {planet_name}")
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        result = swe.calc_ut(jd, planet_id, flags)
        longitude = result[0][0]
        speed = result[0][3]
        if longitude < 0:
            longitude += 360
        is_retro = speed < 0
        if planet_name == "Rahu":
            is_retro = True
        return longitude, is_retro

    # Fallback mean-motion ephemeris
    d = jd - 2451545.0
    if planet_name not in MEAN_LONGITUDE:
        raise ValueError(f"Unsupported planet for fallback ephemeris: {planet_name}")

    l0, n = MEAN_LONGITUDE[planet_name]
    tropical_long = (l0 + n * d) % 360
    ayanamsa = get_ayanamsa(jd)
    sidereal_long = (tropical_long - ayanamsa) % 360
    is_retro = _approx_retrograde(planet_name, d)
    if planet_name == "Rahu":
        is_retro = True
    return sidereal_long, is_retro


def longitude_to_sign(longitude: float) -> Tuple[str, float]:
    """Convert longitude to zodiac sign and degree within sign."""
    sign_index = int(longitude / 30) % 12
    degree_in_sign = longitude % 30
    return SIGNS[sign_index], degree_in_sign


def longitude_to_nakshatra(longitude: float) -> Tuple[str, int, str]:
    """Convert longitude to nakshatra, pada, and nakshatra lord."""
    nak_index = int(longitude / (360 / 27)) % 27
    pada = int((longitude % (360 / 27)) / (360 / 108)) + 1
    pada = min(pada, 4)
    name, lord = NAKSHATRAS[nak_index]
    return name, pada, lord


def calculate_house_from_moon(planet_sign: str, moon_sign: str) -> int:
    """Calculate which house a planet is in relative to Moon sign."""
    planet_idx = SIGNS.index(planet_sign)
    moon_idx = SIGNS.index(moon_sign)
    house = ((planet_idx - moon_idx) % 12) + 1
    return house


# ═══════════════════════════════════════════════════════════════
# HIGH-LEVEL FUNCTIONS (Used by API routes)
# ═══════════════════════════════════════════════════════════════


def get_all_planet_positions(
    dt: datetime,
    birth_dt: Optional[datetime] = None
) -> Dict[str, PlanetPosition]:
    """
    Calculate sidereal positions of all planets for a given datetime.
    If birth_dt provided, also calculates houses relative to birth Moon.
    """
    jd = datetime_to_jd(dt)
    positions: Dict[str, PlanetPosition] = {}

    # Calculate birth Moon for house calculation
    birth_moon_sign = None
    if birth_dt:
        birth_jd = datetime_to_jd(birth_dt)
        moon_long, _ = get_sidereal_position("Moon", birth_jd)
        birth_moon_sign, _ = longitude_to_sign(moon_long)

    for name in PLANETS:
        if name == "Ketu":
            # Ketu is 180° from Rahu
            rahu_pos = positions.get("Rahu")
            if rahu_pos:
                ketu_long = (rahu_pos.longitude + 180) % 360
                sign, degree = longitude_to_sign(ketu_long)
                nak, pada, _ = longitude_to_nakshatra(ketu_long)
                house = None
                if birth_moon_sign:
                    house = calculate_house_from_moon(sign, birth_moon_sign)
                positions["Ketu"] = PlanetPosition(
                    planet="Ketu", longitude=ketu_long, sign=sign,
                    sign_degree=round(degree, 2), nakshatra=nak,
                    nakshatra_pada=pada, is_retrograde=True,
                    house=house
                )
            continue

        longitude, is_retro = get_sidereal_position(name, jd)
        sign, degree = longitude_to_sign(longitude)
        nak, pada, _ = longitude_to_nakshatra(longitude)

        house = None
        if birth_moon_sign:
            house = calculate_house_from_moon(sign, birth_moon_sign)

        # Rahu is always considered retrograde in Vedic astrology
        if name == "Rahu":
            is_retro = True

        positions[name] = PlanetPosition(
            planet=name, longitude=longitude, sign=sign,
            sign_degree=round(degree, 2), nakshatra=nak,
            nakshatra_pada=pada, is_retrograde=is_retro,
            house=house
        )

    return positions


def get_current_transits(user_sign: str, user_dob: date) -> List[TransitInfo]:
    """Get current planetary transits relative to user's Moon sign."""
    now = datetime.utcnow()
    birth_dt = datetime.combine(user_dob, time(12, 0))  # Default noon if no birth time

    positions = get_all_planet_positions(now, birth_dt)

    # Get Moon sign from birth chart
    birth_jd = datetime_to_jd(birth_dt)
    moon_long, _ = get_sidereal_position("Moon", birth_jd)
    moon_sign, _ = longitude_to_sign(moon_long)

    transits = []
    sun_long = positions["Sun"].longitude

    for name, pos in positions.items():
        house = calculate_house_from_moon(pos.sign, moon_sign)

        # Check combustion (within 6° of Sun for most planets)
        is_combust = False
        if name not in ("Sun", "Rahu", "Ketu"):
            diff = abs(pos.longitude - sun_long)
            if diff > 180:
                diff = 360 - diff
            combust_threshold = 6 if name != "Moon" else 12
            is_combust = diff < combust_threshold

        # Determine key aspects
        aspects = []
        for other_name, other_pos in positions.items():
            if other_name == name:
                continue
            diff = abs(pos.longitude - other_pos.longitude)
            if diff > 180:
                diff = 360 - diff
            # Check major aspects (conjunction, opposition, trine, square)
            if diff < 8:
                aspects.append(f"conjunct {other_name}")
            elif abs(diff - 180) < 8:
                aspects.append(f"opposite {other_name}")
            elif abs(diff - 120) < 8:
                aspects.append(f"trine {other_name}")
            elif abs(diff - 90) < 8:
                aspects.append(f"square {other_name}")

        transits.append(TransitInfo(
            planet=name,
            sign=pos.sign,
            house_from_moon=house,
            is_retrograde=pos.is_retrograde,
            is_combust=is_combust,
            aspect_info=", ".join(aspects[:3]) if aspects else "No major aspects"
        ))

    return transits


def calculate_cosmic_battery(user_sign: str, user_dob: date) -> CosmicBattery:
    """
    Calculate the Cosmic Battery percentage based on current transits.
    """
    transits = get_current_transits(user_sign, user_dob)
    score = 60  # Start neutral
    factors = []

    for t in transits:
        # Moon transit (most important for daily energy)
        if t.planet == "Moon":
            if t.house_from_moon in [1, 4, 5, 7, 9, 10, 11]:
                score += 12
                factors.append(f"Moon in {t.house_from_moon}th house (favorable) ✨")
            elif t.house_from_moon in [6, 8, 12]:
                score -= 15
                factors.append(f"Moon in {t.house_from_moon}th house (challenging) ⚠️")
            else:
                score += 3
                factors.append(f"Moon in {t.house_from_moon}th house (neutral)")

        # Jupiter (great benefic)
        elif t.planet == "Jupiter":
            if t.house_from_moon in [1, 5, 9, 11]:
                score += 10
                factors.append(f"Jupiter blessing {t.house_from_moon}th house (excellent) 🌟")
            elif t.house_from_moon in [6, 8, 12]:
                score -= 5
                factors.append(f"Jupiter in {t.house_from_moon}th house (muted benefits)")

        # Saturn (taskmaster)
        elif t.planet == "Saturn":
            if t.house_from_moon in [3, 6, 11]:
                score += 5
                factors.append(f"Saturn in {t.house_from_moon}th house (productive)")
            elif t.house_from_moon in [1, 4, 7, 8, 10, 12]:
                score -= 10
                factors.append(f"Saturn in {t.house_from_moon}th house (heavy energy) 🪨")

        # Mars
        elif t.planet == "Mars":
            if t.house_from_moon in [3, 6, 10, 11]:
                score += 6
                factors.append(f"Mars energizing {t.house_from_moon}th house (drive) 🔥")
            elif t.house_from_moon in [1, 4, 7, 8, 12]:
                score -= 8
                factors.append(f"Mars agitating {t.house_from_moon}th house (tension)")

        # Venus
        elif t.planet == "Venus":
            if t.house_from_moon in [1, 4, 5, 7, 9, 11]:
                score += 5
                factors.append(f"Venus gracing {t.house_from_moon}th house (pleasure) 💫")

        # Mercury retrograde penalty
        elif t.planet == "Mercury" and t.is_retrograde:
            score -= 7
            factors.append("Mercury retrograde (communication disrupted) ☿️")

        # Rahu/Ketu (always cause some chaos)
        elif t.planet == "Rahu":
            if t.house_from_moon in [3, 6, 10, 11]:
                score += 3
                factors.append(f"Rahu in {t.house_from_moon}th (amplifying ambition)")
            else:
                score -= 5
                factors.append(f"Rahu in {t.house_from_moon}th (creating confusion)")

    # Clamp score
    score = max(5, min(98, score))

    # Determine level and message
    if score >= 80:
        level = "peak"
        message = "Star Power at PEAK. The cosmos is literally your hype person today. Ask for that raise, confess your feelings, take the risk."
    elif score >= 60:
        level = "good"
        message = "Cosmic vibes are strong. Good day for decisions. Trust your gut — it's cosmically calibrated right now."
    elif score >= 40:
        level = "neutral"
        message = "Mixed energy day. Not bad, not amazing. Stick to routine. Don't start fights or situationships."
    elif score >= 20:
        level = "low"
        message = "Low energy day. Self-care mode activated. Cancel plans guilt-free. The stars say rest."
    else:
        level = "critical"
        message = "CRITICAL LOW. Do NOT engage. Don't text, don't argue, don't even look at your ex's stories. Hibernate."

    return CosmicBattery(
        percentage=score,
        level=level,
        factors=factors[:5],
        message=message
    )


def format_planetary_context(user_sign: str, user_dob: date) -> str:
    """
    Generate a human-readable planetary context string to inject into AI prompts.
    """
    transits = get_current_transits(user_sign, user_dob)
    now = datetime.utcnow()

    lines = [f"Current Date: {now.strftime('%B %d, %Y %H:%M UTC')}"]
    lines.append(f"User's Sun Sign: {user_sign.capitalize()}")

    # Get birth Moon sign
    birth_dt = datetime.combine(user_dob, time(12, 0))
    birth_jd = datetime_to_jd(birth_dt)
    moon_long, _ = get_sidereal_position("Moon", birth_jd)
    moon_sign, _ = longitude_to_sign(moon_long)
    moon_nak, moon_pada, _ = longitude_to_nakshatra(moon_long)

    lines.append(f"User's Moon Sign (Rashi): {moon_sign}")
    lines.append(f"User's Birth Nakshatra: {moon_nak} (Pada {moon_pada})")
    lines.append("")
    lines.append("CURRENT PLANETARY TRANSITS (Sidereal/Lahiri):")
    lines.append("-" * 50)

    for t in transits:
        retro = " [RETROGRADE]" if t.is_retrograde else ""
        combust = " [COMBUST]" if t.is_combust else ""
        line = f"  {t.planet}: {t.sign}{retro}{combust}"
        line += f" — {t.house_from_moon}th house from Moon"
        if t.aspect_info != "No major aspects":
            line += f" | Aspects: {t.aspect_info}"
        lines.append(line)

    # Add battery info
    battery = calculate_cosmic_battery(user_sign, user_dob)
    lines.append("")
    lines.append(f"COSMIC BATTERY: {battery.percentage}% ({battery.level})")
    for f in battery.factors:
        lines.append(f"  • {f}")

    return "\n".join(lines)


def get_sign_from_dob(dob: date) -> str:
    """Calculate Sun sign from date of birth (Western/Tropical - approximate)."""
    month, day = dob.month, dob.day
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "aries"
    if (month == 4 and day >= 20) or (month == 5 and day <= 20): return "taurus"
    if (month == 5 and day >= 21) or (month == 6 and day <= 20): return "gemini"
    if (month == 6 and day >= 21) or (month == 7 and day <= 22): return "cancer"
    if (month == 7 and day >= 23) or (month == 8 and day <= 22): return "leo"
    if (month == 8 and day >= 23) or (month == 9 and day <= 22): return "virgo"
    if (month == 9 and day >= 23) or (month == 10 and day <= 22): return "libra"
    if (month == 10 and day >= 23) or (month == 11 and day <= 21): return "scorpio"
    if (month == 11 and day >= 22) or (month == 12 and day <= 21): return "sagittarius"
    if (month == 12 and day >= 22) or (month == 1 and day <= 19): return "capricorn"
    if (month == 1 and day >= 20) or (month == 2 and day <= 18): return "aquarius"
    return "pisces"


def get_transits_at_timestamp(timestamp: datetime, user_dob: date) -> str:
    """Get planetary positions at a specific timestamp (for Receipts Judge)."""
    birth_dt = datetime.combine(user_dob, time(12, 0))
    positions = get_all_planet_positions(timestamp, birth_dt)

    lines = [f"Planetary positions at {timestamp.strftime('%I:%M %p on %B %d, %Y')}: "]
    for name, pos in positions.items():
        retro = " (R)" if pos.is_retrograde else ""
        lines.append(f"  {name}: {pos.sign} {pos.sign_degree}°{retro} in {pos.nakshatra}")

    return "\n".join(lines)
