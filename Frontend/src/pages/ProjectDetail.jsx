import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getProject, deleteProject, duplicateProject } from '../services/projects';
import { createGeneration } from '../services/generations';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import './ProjectDetail.css';

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showDelete, setShowDelete] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getProject(id);
      setProject(data);
    } catch {
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await createGeneration({ project_id: id });
      await load();
    } catch {
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteProject(id);
      navigate('/dashboard');
    } catch {}
  };

  const handleDuplicate = async () => {
    try {
      const data = await duplicateProject(id);
      navigate(`/project/${data.id}`);
    } catch {}
  };

  if (loading) return <div className="project-detail-loading container">Loading...</div>;
  if (!project) return null;

  return (
    <div className="project-detail container">
      <div className="project-detail-head">
        <div>
          <div className="project-detail-breadcrumb">
            <span onClick={() => navigate('/dashboard')}>Projects</span>
            <span>/</span>
            <span>{project.title}</span>
          </div>
          <div className="project-detail-title-row">
            <h2>{project.title}</h2>
            <Badge variant={project.status === 'completed' ? 'success' : project.status === 'generating' ? 'warning' : 'default'}>
              {project.status}
            </Badge>
          </div>
          <p className="project-detail-meta">{project.style.replace(/_/g, ' ')} &middot; {new Date(project.created_at).toLocaleDateString()}</p>
          {project.prompt && <p className="project-detail-prompt">"{project.prompt}"</p>}
        </div>
        <div className="project-detail-actions">
          <Button variant="secondary" size="sm" onClick={handleDuplicate}>Duplicate</Button>
          <Button size="sm" loading={generating} onClick={handleGenerate}>Generate</Button>
          <Button variant="danger" size="sm" onClick={() => setShowDelete(true)}>Delete</Button>
        </div>
      </div>

      <div className="project-detail-generations">
        {project.generations?.length === 0 ? (
          <div className="project-detail-empty">
            <h3>No generations yet</h3>
            <p>Click "Generate" to create AI thumbnails for this project.</p>
          </div>
        ) : (
          <div className="project-detail-grid">
            {project.generations.map((gen) => (
              <Card key={gen.id} hover onClick={() => navigate(`/generation/${gen.id}`)} className="project-detail-gen">
                {gen.image_url ? (
                  <div className="project-detail-gen-img-wrap">
                    <img src={gen.image_url} alt={gen.ai_prompt} className="project-detail-gen-img" />
                    {gen.ai_score != null && (
                      <div className="project-detail-gen-score">{gen.ai_score}</div>
                    )}
                  </div>
                ) : (
                  <div className="project-detail-gen-placeholder">
                    {gen.status === 'generating' ? 'Generating...' : gen.status}
                  </div>
                )}
                <div className="project-detail-gen-info">
                  <Badge variant={gen.status === 'completed' ? 'success' : gen.status === 'generating' ? 'warning' : 'error'}>
                    {gen.status}
                  </Badge>
                  <span className="project-detail-gen-date">{new Date(gen.created_at).toLocaleDateString()}</span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      <Modal open={showDelete} onClose={() => setShowDelete(false)} title="Delete Project">
        <p>Are you sure you want to delete "{project.title}"? This action cannot be undone.</p>
        <div className="project-detail-modal-actions">
          <Button variant="secondary" onClick={() => setShowDelete(false)}>Cancel</Button>
          <Button variant="danger" onClick={handleDelete}>Delete</Button>
        </div>
      </Modal>
    </div>
  );
}
