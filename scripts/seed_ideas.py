"""
Seed Script: Ideas Management System
Populates database with 10 genres and 100 video ideas (10 per genre)

Run with: python scripts/seed_ideas.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from models import SessionLocal, Genre, VideoIdea, IdeaPrompt

# Load environment variables
load_dotenv()


# Genre data with 10 curated genres
GENRES_DATA = [
    {
        "name": "Classical",
        "slug": "classical",
        "description": "Timeless classical music from various eras including Baroque, Romantic, and Modern periods",
        "color": "#8B7355",
        "icon_name": "violin",
        "default_duration_minutes": 75,
        "sort_order": 1,
    },
    {
        "name": "Lo-fi Hip Hop",
        "slug": "lo-fi-hip-hop",
        "description": "Relaxed, downtempo beats perfect for studying, working, or unwinding",
        "color": "#FF6B9D",
        "icon_name": "headphones",
        "default_duration_minutes": 70,
        "sort_order": 2,
    },
    {
        "name": "Jazz",
        "slug": "jazz",
        "description": "Smooth jazz, bebop, and contemporary jazz fusion for sophisticated listening",
        "color": "#4A90E2",
        "icon_name": "saxophone",
        "default_duration_minutes": 80,
        "sort_order": 3,
    },
    {
        "name": "Ambient",
        "slug": "ambient",
        "description": "Atmospheric, meditative soundscapes for relaxation and focus",
        "color": "#7ED321",
        "icon_name": "waves",
        "default_duration_minutes": 90,
        "sort_order": 4,
    },
    {
        "name": "Electronic Chill",
        "slug": "electronic-chill",
        "description": "Downtempo electronic music with ethereal synths and mellow beats",
        "color": "#9013FE",
        "icon_name": "synth",
        "default_duration_minutes": 70,
        "sort_order": 5,
    },
    {
        "name": "Acoustic",
        "slug": "acoustic",
        "description": "Organic acoustic guitar, piano, and instrumental compositions",
        "color": "#D0A64A",
        "icon_name": "guitar",
        "default_duration_minutes": 75,
        "sort_order": 6,
    },
    {
        "name": "Cinematic",
        "slug": "cinematic",
        "description": "Epic orchestral and cinematic scores for dramatic atmosphere",
        "color": "#B8860B",
        "icon_name": "film",
        "default_duration_minutes": 85,
        "sort_order": 7,
    },
    {
        "name": "Nature Sounds",
        "slug": "nature-sounds",
        "description": "Natural soundscapes including rain, forest, ocean, and wildlife",
        "color": "#50C878",
        "icon_name": "leaf",
        "default_duration_minutes": 90,
        "sort_order": 8,
    },
    {
        "name": "Meditation",
        "slug": "meditation",
        "description": "Calming music and tones for meditation, yoga, and mindfulness practices",
        "color": "#9B59B6",
        "icon_name": "lotus",
        "default_duration_minutes": 80,
        "sort_order": 9,
    },
    {
        "name": "Study Music",
        "slug": "study-music",
        "description": "Concentration-enhancing background music for productivity and learning",
        "color": "#3498DB",
        "icon_name": "book",
        "default_duration_minutes": 75,
        "sort_order": 10,
    },
]


# Video ideas data: 10 ideas per genre (100 total)
VIDEO_IDEAS_DATA = {
    "classical": [
        {"title": "Regency Era Ballroom Ambience", "niche": "Historical Classical - Regency", "moods": ["elegant", "calm", "romantic"], "desc": "Elegant classical pieces evoking the grandeur of Regency ballrooms with waltzes and minuets"},
        {"title": "Baroque Chamber Music Collection", "niche": "Baroque Classical", "moods": ["focused", "sophisticated", "uplifting"], "desc": "Intimate baroque chamber works featuring harpsichord, strings, and woodwinds"},
        {"title": "Romantic Piano Nocturnes", "niche": "Romantic Piano", "moods": ["calm", "emotional", "atmospheric"], "desc": "Expressive romantic-era piano compositions perfect for evening relaxation"},
        {"title": "Medieval Court Music Anthology", "niche": "Medieval Classical", "moods": ["historical", "atmospheric", "calm"], "desc": "Authentic medieval court music with period instruments and ancient melodies"},
        {"title": "Victorian Tea Room Classics", "niche": "Victorian Classical", "moods": ["elegant", "calm", "sophisticated"], "desc": "Refined classical selections perfect for afternoon tea in Victorian style"},
        {"title": "Renaissance Festival Soundscape", "niche": "Renaissance Classical", "moods": ["festive", "historical", "uplifting"], "desc": "Lively Renaissance music featuring lutes, recorders, and period ensembles"},
        {"title": "Imperial Palace Orchestra", "niche": "Classical Orchestral", "moods": ["grand", "majestic", "elegant"], "desc": "Grand orchestral works evoking the splendor of imperial courts"},
        {"title": "Candlelit Cathedral Chorales", "niche": "Sacred Classical", "moods": ["spiritual", "calm", "atmospheric"], "desc": "Serene choral works and organ music in cathedral acoustics"},
        {"title": "Autumn Countryside Piano", "niche": "Classical Piano - Seasonal", "moods": ["nostalgic", "calm", "emotional"], "desc": "Contemplative piano pieces inspired by autumn landscapes"},
        {"title": "Royal Library Study Music", "niche": "Classical Study", "moods": ["focused", "calm", "sophisticated"], "desc": "Concentration-enhancing classical music for studying in scholarly atmosphere"},
    ],
    "lo-fi-hip-hop": [
        {"title": "Rainy Tokyo Night Beats", "niche": "Lo-fi - Urban Japan", "moods": ["calm", "atmospheric", "nostalgic"], "desc": "Mellow beats with rain sounds capturing late-night Tokyo vibes"},
        {"title": "Coffee Shop Study Session", "niche": "Lo-fi Study", "moods": ["focused", "calm", "relaxing"], "desc": "Smooth lo-fi beats perfect for café studying and productivity"},
        {"title": "Sunset Drive Chill Beats", "niche": "Lo-fi - Travel", "moods": ["relaxing", "uplifting", "calm"], "desc": "Laid-back beats for sunset drives and evening wind-downs"},
        {"title": "Bedroom Producer Collection", "niche": "Lo-fi Instrumental", "moods": ["creative", "calm", "atmospheric"], "desc": "Raw, authentic bedroom-produced lo-fi with vinyl crackle"},
        {"title": "Late Night Coding Session", "niche": "Lo-fi Productivity", "moods": ["focused", "energetic", "calm"], "desc": "Energizing lo-fi beats for late-night programming and creative work"},
        {"title": "Autumn Leaves Lo-fi Mix", "niche": "Lo-fi - Seasonal", "moods": ["nostalgic", "calm", "atmospheric"], "desc": "Warm lo-fi beats capturing the essence of fall"},
        {"title": "City Lights After Dark", "niche": "Lo-fi Urban", "moods": ["atmospheric", "calm", "cinematic"], "desc": "Urban lo-fi capturing the ambiance of city nights"},
        {"title": "Morning Routine Beats", "niche": "Lo-fi - Daily Life", "moods": ["uplifting", "calm", "energetic"], "desc": "Gentle lo-fi beats to ease into your morning"},
        {"title": "Anime Study Lounge", "niche": "Lo-fi - Anime Inspired", "moods": ["focused", "nostalgic", "calm"], "desc": "Lo-fi beats with anime-inspired melodies for studying"},
        {"title": "Retro Game Console Beats", "niche": "Lo-fi - Gaming", "moods": ["nostalgic", "energetic", "atmospheric"], "desc": "8-bit inspired lo-fi with vintage gaming aesthetics"},
    ],
    "jazz": [
        {"title": "Smoky Jazz Club After Hours", "niche": "Jazz Club", "moods": ["sophisticated", "calm", "atmospheric"], "desc": "Intimate jazz trio capturing late-night club atmosphere"},
        {"title": "Bossa Nova Beach Sunset", "niche": "Bossa Nova", "moods": ["relaxing", "uplifting", "romantic"], "desc": "Smooth bossa nova rhythms perfect for tropical relaxation"},
        {"title": "Bebop City Chronicles", "niche": "Bebop Jazz", "moods": ["energetic", "sophisticated", "uplifting"], "desc": "Fast-paced bebop featuring virtuoso improvisation"},
        {"title": "Cool Jazz Midnight Drive", "niche": "Cool Jazz", "moods": ["calm", "sophisticated", "atmospheric"], "desc": "Smooth cool jazz perfect for late-night drives"},
        {"title": "New Orleans Street Jazz", "niche": "Traditional Jazz", "moods": ["uplifting", "festive", "energetic"], "desc": "Lively traditional jazz capturing New Orleans spirit"},
        {"title": "Contemporary Jazz Fusion", "niche": "Jazz Fusion", "moods": ["sophisticated", "energetic", "creative"], "desc": "Modern jazz fusion blending electric and acoustic elements"},
        {"title": "Vintage Swing Dance Hall", "niche": "Swing Jazz", "moods": ["uplifting", "energetic", "festive"], "desc": "Classic swing era big band for dancing and celebration"},
        {"title": "Latin Jazz Fiesta", "niche": "Latin Jazz", "moods": ["energetic", "festive", "uplifting"], "desc": "Vibrant Latin jazz with Afro-Cuban rhythms"},
        {"title": "Autumn Jazz Standards", "niche": "Jazz Standards", "moods": ["nostalgic", "calm", "romantic"], "desc": "Timeless jazz standards perfect for fall evenings"},
        {"title": "Morning Coffee Jazz Piano", "niche": "Jazz Piano", "moods": ["calm", "uplifting", "sophisticated"], "desc": "Gentle jazz piano for peaceful morning coffee"},
    ],
    "ambient": [
        {"title": "Deep Space Exploration", "niche": "Ambient - Space", "moods": ["atmospheric", "calm", "cinematic"], "desc": "Cosmic soundscapes for interstellar meditation"},
        {"title": "Underwater Ocean Depths", "niche": "Ambient - Aquatic", "moods": ["calm", "mysterious", "atmospheric"], "desc": "Immersive underwater ambient sounds and drones"},
        {"title": "Ancient Forest Meditation", "niche": "Ambient - Nature", "moods": ["calm", "spiritual", "atmospheric"], "desc": "Ethereal forest ambience for deep meditation"},
        {"title": "Northern Lights Soundscape", "niche": "Ambient - Atmospheric", "moods": ["atmospheric", "calm", "cinematic"], "desc": "Shimmering ambient tones inspired by aurora borealis"},
        {"title": "Desert Night Sky", "niche": "Ambient - Desert", "moods": ["calm", "atmospheric", "mysterious"], "desc": "Vast desert soundscapes under starlit skies"},
        {"title": "Glacial Cave Resonance", "niche": "Ambient - Arctic", "moods": ["atmospheric", "calm", "cinematic"], "desc": "Crystalline ambient echoes from frozen landscapes"},
        {"title": "Monastery Bell Meditation", "niche": "Ambient - Spiritual", "moods": ["spiritual", "calm", "atmospheric"], "desc": "Sacred ambient tones with Tibetan singing bowls"},
        {"title": "Nebula Dreams", "niche": "Ambient - Cosmic", "moods": ["atmospheric", "calm", "dreamy"], "desc": "Ethereal cosmic ambient for lucid dreaming"},
        {"title": "Mountain Peak Solitude", "niche": "Ambient - Mountain", "moods": ["calm", "atmospheric", "peaceful"], "desc": "High-altitude ambient with wind and space"},
        {"title": "Eternal Horizon", "niche": "Ambient - Abstract", "moods": ["atmospheric", "calm", "meditative"], "desc": "Timeless ambient drones for contemplation"},
    ],
    "electronic-chill": [
        {"title": "Synthwave Sunset Boulevard", "niche": "Synthwave Chill", "moods": ["nostalgic", "calm", "atmospheric"], "desc": "Retro synthwave with mellow 80s-inspired vibes"},
        {"title": "Tropical House Paradise", "niche": "Tropical House", "moods": ["uplifting", "relaxing", "atmospheric"], "desc": "Breezy tropical house beats for island relaxation"},
        {"title": "Future Garage Nights", "niche": "Future Garage", "moods": ["atmospheric", "calm", "mysterious"], "desc": "Deep future garage with atmospheric textures"},
        {"title": "Chillwave Memory Lane", "niche": "Chillwave", "moods": ["nostalgic", "calm", "dreamy"], "desc": "Nostalgic chillwave evoking summer memories"},
        {"title": "Downtempo Electronica", "niche": "Downtempo", "moods": ["calm", "atmospheric", "sophisticated"], "desc": "Sophisticated downtempo beats and organic textures"},
        {"title": "Liquid Drum & Bass Flow", "niche": "Liquid DnB", "moods": ["calm", "energetic", "atmospheric"], "desc": "Smooth liquid drum & bass for focused energy"},
        {"title": "Ambient Techno Journey", "niche": "Ambient Techno", "moods": ["atmospheric", "calm", "hypnotic"], "desc": "Minimal ambient techno with deep grooves"},
        {"title": "Chillstep Dreamscape", "niche": "Chillstep", "moods": ["calm", "emotional", "atmospheric"], "desc": "Melodic chillstep with ethereal vocals"},
        {"title": "Deep House Meditation", "niche": "Deep House", "moods": ["calm", "hypnotic", "atmospheric"], "desc": "Hypnotic deep house for meditative states"},
        {"title": "Trip Hop Chronicles", "niche": "Trip Hop", "moods": ["mysterious", "calm", "atmospheric"], "desc": "Dark trip hop beats with cinematic elements"},
    ],
    "acoustic": [
        {"title": "Fingerstyle Guitar Cafe", "niche": "Acoustic Guitar", "moods": ["calm", "uplifting", "warm"], "desc": "Intricate fingerstyle guitar for café ambiance"},
        {"title": "Celtic Harp & Flute Tales", "niche": "Celtic Acoustic", "moods": ["mystical", "calm", "uplifting"], "desc": "Traditional Celtic melodies on harp and flute"},
        {"title": "Spanish Guitar Sunset", "niche": "Spanish Guitar", "moods": ["romantic", "warm", "elegant"], "desc": "Passionate Spanish guitar for evening romance"},
        {"title": "Piano & Cello Duets", "niche": "Classical Acoustic", "moods": ["emotional", "calm", "elegant"], "desc": "Intimate piano and cello conversations"},
        {"title": "Folk Mandolin Journey", "niche": "Folk Acoustic", "moods": ["uplifting", "warm", "nostalgic"], "desc": "Cheerful folk melodies featuring mandolin"},
        {"title": "Ukulele Island Breeze", "niche": "Ukulele", "moods": ["uplifting", "relaxing", "warm"], "desc": "Lighthearted ukulele melodies from the islands"},
        {"title": "Banjo Appalachian Trails", "niche": "Bluegrass Acoustic", "moods": ["energetic", "uplifting", "warm"], "desc": "Lively bluegrass banjo and fiddle tunes"},
        {"title": "Sitar Meditation Ragas", "niche": "Indian Classical", "moods": ["spiritual", "calm", "atmospheric"], "desc": "Traditional Indian ragas on sitar for meditation"},
        {"title": "Cajón & Acoustic Rhythm", "niche": "World Acoustic", "moods": ["energetic", "warm", "uplifting"], "desc": "Percussive acoustic featuring cajón and guitar"},
        {"title": "Steel Pan Caribbean Dreams", "niche": "Caribbean Acoustic", "moods": ["uplifting", "relaxing", "warm"], "desc": "Tropical steel pan melodies from the Caribbean"},
    ],
    "cinematic": [
        {"title": "Epic Orchestral Adventure", "niche": "Epic Cinematic", "moods": ["majestic", "energetic", "uplifting"], "desc": "Grand orchestral scores for heroic adventures"},
        {"title": "Dark Fantasy Soundscapes", "niche": "Fantasy Cinematic", "moods": ["mysterious", "atmospheric", "dramatic"], "desc": "Haunting fantasy themes with choir and orchestra"},
        {"title": "Sci-Fi Space Opera", "niche": "Sci-Fi Cinematic", "moods": ["cinematic", "atmospheric", "majestic"], "desc": "Futuristic orchestral music for space exploration"},
        {"title": "Emotional Piano Drama", "niche": "Drama Cinematic", "moods": ["emotional", "calm", "reflective"], "desc": "Poignant piano-led scores for dramatic moments"},
        {"title": "Action Chase Sequences", "niche": "Action Cinematic", "moods": ["energetic", "intense", "dramatic"], "desc": "High-octane orchestral music for chase scenes"},
        {"title": "Medieval Battle Hymns", "niche": "Medieval Cinematic", "moods": ["epic", "dramatic", "majestic"], "desc": "Powerful medieval war drums and brass"},
        {"title": "Romantic Film Scores", "niche": "Romance Cinematic", "moods": ["romantic", "emotional", "uplifting"], "desc": "Sweeping romantic themes with strings"},
        {"title": "Horror Tension & Dread", "niche": "Horror Cinematic", "moods": ["mysterious", "dark", "atmospheric"], "desc": "Suspenseful horror scores with dissonant strings"},
        {"title": "Western Frontier Ballads", "niche": "Western Cinematic", "moods": ["dramatic", "nostalgic", "majestic"], "desc": "Classic Western themes with harmonica and guitar"},
        {"title": "Inspirational Documentary Themes", "niche": "Documentary Cinematic", "moods": ["uplifting", "emotional", "reflective"], "desc": "Hopeful orchestral music for documentaries"},
    ],
    "nature-sounds": [
        {"title": "Tropical Rainforest Ambience", "niche": "Rainforest Sounds", "moods": ["calm", "atmospheric", "natural"], "desc": "Immersive tropical jungle with birds and rain"},
        {"title": "Ocean Waves Meditation", "niche": "Ocean Sounds", "moods": ["calm", "relaxing", "natural"], "desc": "Gentle ocean waves on sandy beach"},
        {"title": "Mountain Stream & Birds", "niche": "Mountain Sounds", "moods": ["calm", "peaceful", "natural"], "desc": "Babbling brook with mountain bird songs"},
        {"title": "Thunderstorm & Rain", "niche": "Storm Sounds", "moods": ["atmospheric", "calm", "powerful"], "desc": "Powerful thunderstorm with heavy rain"},
        {"title": "Forest Dawn Chorus", "niche": "Forest Sounds", "moods": ["uplifting", "calm", "natural"], "desc": "Morning birdsong in deciduous forest"},
        {"title": "Desert Wind & Silence", "niche": "Desert Sounds", "moods": ["calm", "mysterious", "atmospheric"], "desc": "Vast desert with gentle wind and space"},
        {"title": "Winter Snowfall Quiet", "niche": "Winter Sounds", "moods": ["calm", "peaceful", "serene"], "desc": "Silent snowfall in winter forest"},
        {"title": "Savannah Wildlife", "niche": "Savannah Sounds", "moods": ["atmospheric", "natural", "exotic"], "desc": "African savannah with distant animal calls"},
        {"title": "Coastal Seabirds & Surf", "niche": "Coastal Sounds", "moods": ["calm", "natural", "peaceful"], "desc": "Seagulls and gentle surf on rocky coast"},
        {"title": "Bamboo Forest Breeze", "niche": "Asian Nature", "moods": ["calm", "peaceful", "mystical"], "desc": "Wind through bamboo grove with subtle chimes"},
    ],
    "meditation": [
        {"title": "Tibetan Singing Bowl Journey", "niche": "Tibetan Meditation", "moods": ["spiritual", "calm", "healing"], "desc": "Sacred Tibetan bowls for deep meditation"},
        {"title": "432 Hz Healing Frequencies", "niche": "Frequency Healing", "moods": ["healing", "calm", "spiritual"], "desc": "Pure 432 Hz tones for cellular healing"},
        {"title": "Chakra Balancing Meditation", "niche": "Chakra Meditation", "moods": ["spiritual", "healing", "calm"], "desc": "Binaural beats tuned to each chakra center"},
        {"title": "Zen Garden Meditation", "niche": "Zen Meditation", "moods": ["calm", "peaceful", "spiritual"], "desc": "Minimalist tones inspired by Zen philosophy"},
        {"title": "Guided Breathing Ambient", "niche": "Breathwork", "moods": ["calm", "healing", "focused"], "desc": "Ambient music synchronized with breathing patterns"},
        {"title": "Crystal Bowl Healing", "niche": "Sound Healing", "moods": ["healing", "spiritual", "calm"], "desc": "Quartz crystal singing bowls for energy healing"},
        {"title": "Binaural Theta Waves", "niche": "Brainwave Entrainment", "moods": ["deep", "calm", "meditative"], "desc": "Theta wave binaural beats for deep meditation"},
        {"title": "Kundalini Awakening Tones", "niche": "Kundalini Meditation", "moods": ["spiritual", "energetic", "transformative"], "desc": "Powerful tones for kundalini energy work"},
        {"title": "Mindfulness Bell Meditation", "niche": "Mindfulness", "moods": ["calm", "present", "peaceful"], "desc": "Gentle bells for mindfulness practice"},
        {"title": "Sacred Mantra Vibrations", "niche": "Mantra Meditation", "moods": ["spiritual", "calm", "sacred"], "desc": "Ancient mantras with harmonic overtones"},
    ],
    "study-music": [
        {"title": "Focus Flow Productivity Mix", "niche": "Study - Productivity", "moods": ["focused", "calm", "energizing"], "desc": "Optimized beats for deep work and concentration"},
        {"title": "Library Study Ambience", "niche": "Study - Classical", "moods": ["calm", "focused", "sophisticated"], "desc": "Classical music perfect for library studying"},
        {"title": "Pomodoro Timer Sessions", "niche": "Study - Time Management", "moods": ["focused", "energetic", "structured"], "desc": "Music synchronized with 25-minute work intervals"},
        {"title": "Math & Science Study", "niche": "Study - STEM", "moods": ["focused", "analytical", "calm"], "desc": "Logic-enhancing music for STEM subjects"},
        {"title": "Creative Writing Session", "niche": "Study - Creative", "moods": ["creative", "calm", "inspiring"], "desc": "Ambient soundscapes for creative writing"},
        {"title": "Language Learning Beats", "niche": "Study - Languages", "moods": ["focused", "calm", "uplifting"], "desc": "Gentle beats for language memorization"},
        {"title": "Exam Preparation Music", "niche": "Study - Exam Prep", "moods": ["calm", "focused", "confident"], "desc": "Stress-reducing music for exam studying"},
        {"title": "Alpha Wave Study Aid", "niche": "Study - Brainwaves", "moods": ["focused", "calm", "enhanced"], "desc": "Alpha frequency binaural beats for learning"},
        {"title": "Reading Comprehension Mix", "niche": "Study - Reading", "moods": ["calm", "focused", "peaceful"], "desc": "Quiet background music for reading"},
        {"title": "Late Night Thesis Writing", "niche": "Study - Research", "moods": ["focused", "calm", "sustained"], "desc": "Long-form ambient for marathon study sessions"},
    ],
}


def create_genres(db):
    """Create all genres in the database"""
    print("\n📋 Creating genres...")

    created_genres = {}

    for genre_data in GENRES_DATA:
        genre = Genre(**genre_data)
        db.add(genre)
        db.flush()  # Get ID without committing
        created_genres[genre_data["slug"]] = genre
        print(f"  ✅ Created genre: {genre.name}")

    db.commit()
    print(f"\n✅ Successfully created {len(created_genres)} genres")

    return created_genres


def create_video_ideas(db, genres):
    """Create all video ideas for each genre"""
    print("\n📋 Creating video ideas...")

    created_ideas = []
    total_count = 0

    for genre_slug, ideas_data in VIDEO_IDEAS_DATA.items():
        genre = genres.get(genre_slug)
        if not genre:
            print(f"  ⚠️  Warning: Genre '{genre_slug}' not found, skipping ideas")
            continue

        print(f"\n  Creating ideas for genre: {genre.name}")

        for idea_data in ideas_data:
            video_idea = VideoIdea(
                genre_id=genre.id,
                title=idea_data["title"],
                description=idea_data["desc"],
                niche_label=idea_data["niche"],
                mood_tags=idea_data["moods"],
                target_duration_minutes=genre.default_duration_minutes,
                num_tracks=20,
                is_template=True,
                is_archived=False,
                times_used=0,
            )
            db.add(video_idea)
            created_ideas.append(video_idea)
            total_count += 1
            print(f"    ✅ {idea_data['title']}")

    db.commit()
    print(f"\n✅ Successfully created {total_count} video ideas across {len(VIDEO_IDEAS_DATA)} genres")

    return created_ideas


def main():
    """Run the seed script"""
    print("=" * 60)
    print("SEED SCRIPT: Ideas Management System")
    print("=" * 60)
    print("\nThis will populate the database with:")
    print("  - 10 curated genres")
    print("  - 100 video ideas (10 per genre)")
    print("\nNote: Prompts can be generated later via the API")
    print("=" * 60)

    # Get database session
    db = SessionLocal()

    try:
        # Check if genres already exist
        existing_genre_count = db.query(Genre).count()
        if existing_genre_count > 0:
            print(f"\n⚠️  Warning: Database already has {existing_genre_count} genres")
            response = input("Do you want to continue? This will add more data. (y/n): ")
            if response.lower() != 'y':
                print("\n❌ Seed script cancelled")
                return

        # Create genres
        genres = create_genres(db)

        # Create video ideas
        ideas = create_video_ideas(db, genres)

        # Summary
        print("\n" + "=" * 60)
        print("✅ SEED COMPLETE!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  - Genres created: {len(genres)}")
        print(f"  - Video ideas created: {len(ideas)}")
        print(f"\n🚀 Next steps:")
        print("  1. Start your FastAPI server: uvicorn main:app --reload")
        print("  2. View genres: GET http://localhost:8000/api/genres")
        print("  3. View ideas: GET http://localhost:8000/api/ideas")
        print("  4. Generate prompts for ideas via POST /api/ideas/{id}/prompts")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
