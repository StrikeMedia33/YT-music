/**
 * TypeScript types for Ideas Management System
 */

export interface Genre {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  color: string | null;
  icon_name: string | null;
  default_duration_minutes: number;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface GenreWithStats extends Genre {
  idea_count: number;
  active_idea_count: number;
}

export interface VideoIdea {
  id: string;
  genre_id: string;
  title: string;
  description: string | null;
  niche_label: string;
  mood_tags: string[];
  target_duration_minutes: number;
  num_tracks: number;
  is_template: boolean;
  is_archived: boolean;
  times_used: number;
  created_at: string;
  updated_at: string;
}

export interface VideoIdeaDetail extends VideoIdea {
  genre: Genre | null;
  prompts: IdeaPrompt | null;
}

export interface IdeaPrompt {
  id: string;
  idea_id: string;
  music_prompts: string[];
  visual_prompts: string[];
  metadata_title: string | null;
  metadata_description: string | null;
  metadata_tags: string[];
  generation_params: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface VideoIdeaCreate {
  title: string;
  description?: string;
  genre_id: string;
  niche_label: string;
  mood_tags?: string[];
  target_duration_minutes?: number;
  num_tracks?: number;
  is_template?: boolean;
}

export interface VideoIdeaUpdate {
  title?: string;
  description?: string;
  genre_id?: string;
  niche_label?: string;
  mood_tags?: string[];
  target_duration_minutes?: number;
  num_tracks?: number;
  is_template?: boolean;
  is_archived?: boolean;
}

export interface IdeaPromptCreate {
  music_prompts: string[];
  visual_prompts: string[];
  metadata_title?: string;
  metadata_description?: string;
  metadata_tags?: string[];
  generation_params?: Record<string, any>;
}

export interface IdeasSearchParams {
  genre_id?: string;
  search?: string;
  mood_tags?: string[];
  is_template?: boolean;
  is_archived?: boolean;
  sort_by?: 'created_at' | 'title' | 'times_used';
  sort_order?: 'asc' | 'desc';
  skip?: number;
  limit?: number;
}
