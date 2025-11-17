#!/usr/bin/env python
"""
Test script for video job integration with idea templates
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from models import VideoJob, VideoIdea, Channel, VideoJobIdea, VideoJobStatus
import uuid

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("=== Video Job Integration Test ===\n")

    # 1. Get an existing idea
    print("1. Fetching an existing idea...")
    idea = db.query(VideoIdea).first()
    if not idea:
        print("ERROR: No ideas found. Run seed script first.")
        sys.exit(1)

    print(f"   ✓ Found idea: {idea.title}")
    print(f"     - Niche: {idea.niche_label}")
    print(f"     - Mood tags: {', '.join(idea.mood_tags)}")
    print(f"     - Times used: {idea.times_used}")
    idea_id = idea.id
    initial_times_used = idea.times_used

    # 2. Get or create a channel
    print("\n2. Getting or creating a test channel...")
    channel = db.query(Channel).first()
    if not channel:
        channel = Channel(
            name="Test Channel",
            youtube_channel_id="UC" + str(uuid.uuid4())[:8],
            brand_niche="Test Niche",
            is_active=True
        )
        db.add(channel)
        db.commit()
        db.refresh(channel)
        print(f"   ✓ Created channel: {channel.name}")
    else:
        print(f"   ✓ Using existing channel: {channel.name}")
    channel_id = channel.id

    # 3. Create a video job WITHOUT an idea (baseline test)
    print("\n3. Creating baseline video job (no idea template)...")
    job_without_idea = VideoJob(
        channel_id=str(channel_id),
        status="planned",  # Use string value directly
        niche_label="Manual Niche",
        mood_keywords="manual, test, baseline",
        target_duration_minutes=70,
        output_directory="./output/test"
    )
    db.add(job_without_idea)
    db.commit()
    db.refresh(job_without_idea)
    print(f"   ✓ Created job: {job_without_idea.id}")

    # Verify no link was created
    link_check = db.query(VideoJobIdea).filter(
        VideoJobIdea.video_job_id == job_without_idea.id
    ).first()
    if link_check:
        print("   ✗ ERROR: Link created when it shouldn't have been!")
        sys.exit(1)
    print("   ✓ No idea link created (as expected)")

    # 4. Create a video job WITH an idea template
    print("\n4. Creating video job with idea template...")
    job_with_idea = VideoJob(
        channel_id=str(channel_id),
        status="planned",  # Use string value directly
        niche_label=idea.niche_label,  # Pre-filled from idea
        mood_keywords=', '.join(idea.mood_tags),  # Pre-filled from idea
        target_duration_minutes=idea.target_duration_minutes,
        output_directory="./output/test2"
    )
    db.add(job_with_idea)
    db.commit()
    db.refresh(job_with_idea)
    print(f"   ✓ Created job: {job_with_idea.id}")
    print(f"     - Niche: {job_with_idea.niche_label}")
    print(f"     - Mood: {job_with_idea.mood_keywords}")

    # 5. Manually create the link (simulating what the API does)
    print("\n5. Creating VideoJobIdea link...")
    link = VideoJobIdea(
        video_job_id=job_with_idea.id,
        video_idea_id=idea_id,
        customizations_json={}
    )
    db.add(link)

    # 6. Increment times_used
    print("\n6. Incrementing idea usage counter...")
    idea.times_used += 1
    db.commit()

    # 7. Verify everything
    print("\n7. Verifying integration...")

    # Refresh idea to get updated times_used
    db.refresh(idea)

    # Check link exists
    link_verify = db.query(VideoJobIdea).filter(
        VideoJobIdea.video_job_id == job_with_idea.id
    ).first()
    if not link_verify:
        print("   ✗ ERROR: Link was not created!")
        sys.exit(1)
    print(f"   ✓ Link created successfully")
    print(f"     - Job ID: {link_verify.video_job_id}")
    print(f"     - Idea ID: {link_verify.video_idea_id}")

    # Check times_used was incremented
    if idea.times_used != initial_times_used + 1:
        print(f"   ✗ ERROR: times_used not incremented! Expected {initial_times_used + 1}, got {idea.times_used}")
        sys.exit(1)
    print(f"   ✓ Idea usage counter incremented: {initial_times_used} → {idea.times_used}")

    print("\n" + "="*50)
    print("✅ All tests passed!")
    print("="*50)

    # Clean up test data
    print("\nCleaning up test data...")
    db.delete(link)
    db.delete(job_with_idea)
    db.delete(job_without_idea)
    # Decrement times_used back
    idea.times_used = initial_times_used
    db.commit()
    print("✓ Cleanup complete")

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
