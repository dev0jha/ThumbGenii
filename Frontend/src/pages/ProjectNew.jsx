import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProject, getStyles } from '../services/projects';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import './ProjectNew.css';

const STYLES = [
  { id: 'youtube_thumbnail', name: 'YouTube Thumbnail' },
  { id: 'gaming', name: 'Gaming' },
  { id: 'tech_review', name: 'Tech Review' },
  { id: 'vlog', name: 'Vlog' },
  { id: 'tutorial', name: 'Tutorial' },
  { id: 'educational', name: 'Educational' },
  { id: 'entertainment', name: 'Entertainment' },
  { id: 'podcast', name: 'Podcast' },
  { id: 'shorts', name: 'Shorts' },
  { id: 'viral_shorts', name: 'Viral Shorts' },
  { id: 'square', name: 'Square' },
  { id: 'instagram', name: 'Instagram' },
  { id: 'linkedin', name: 'LinkedIn' },
  { id: 'twitter', name: 'Twitter/X' },
  { id: 'facebook', name: 'Facebook' },
  { id: 'custom', name: 'Custom' },
];

export default function ProjectNew() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: '',
    prompt: '',
    style: 'youtube_thumbnail',
    video_title: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await createProject(form);
      navigate(`/project/${data.id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="project-new container">
      <div className="project-new-head">
        <div>
          <h2>New Project</h2>
          <p className="project-new-desc">Describe the thumbnail you want to generate</p>
        </div>
      </div>

      <div className="project-new-layout">
        <Card className="project-new-form">
          {error && <div className="project-new-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <Input
              label="Project Title"
              placeholder="e.g. My Awesome Video"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
            <Input
              label="Video Title (optional)"
              placeholder="e.g. I Tried This For 30 Days..."
              value={form.video_title}
              onChange={(e) => setForm({ ...form, video_title: e.target.value })}
            />
            <div className="input-group">
              <label className="input-label">Thumbnail Description / Prompt</label>
              <textarea
                className="input-field project-new-textarea"
                placeholder="Describe the thumbnail you want... e.g. 'A surprised man looking at an explosion behind him, bright orange and blue colors, bold text area on the left'"
                value={form.prompt}
                onChange={(e) => setForm({ ...form, prompt: e.target.value })}
                rows={5}
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Style</label>
              <select
                className="input-field"
                value={form.style}
                onChange={(e) => setForm({ ...form, style: e.target.value })}
              >
                {STYLES.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <Button type="submit" fullWidth size="lg" loading={loading}>
              Create & Generate
            </Button>
          </form>
        </Card>

        <Card className="project-new-tips">
          <h4>Tips for great thumbnails</h4>
          <ul>
            <li>Describe the main subject clearly</li>
            <li>Mention colors, mood, and composition</li>
            <li>Keep the focal point centered</li>
            <li>Avoid text in the image (it's added later)</li>
            <li>Use high-contrast color combinations</li>
            <li>Reference popular styles in your niche</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}
