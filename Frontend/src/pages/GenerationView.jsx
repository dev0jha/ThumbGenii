import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getGeneration, regenerateGeneration, scoreGeneration, exportGeneration } from '../services/generations';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import './GenerationView.css';

export default function GenerationView() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [gen, setGen] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scoring, setScoring] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [exportFormat, setExportFormat] = useState('png');
  const [exportQuality, setExportQuality] = useState(90);
  const [exporting, setExporting] = useState(false);

  const load = async () => {
    try {
      const data = await getGeneration(id);
      setGen(data);
    } catch {
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleScore = async () => {
    setScoring(true);
    try {
      const result = await scoreGeneration(id);
      setGen((prev) => ({
        ...prev,
        ai_score: result.score,
        ai_feedback: result.feedback,
        ctr_prediction: result.ctr_potential,
      }));
    } catch {}
    setScoring(false);
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const result = await regenerateGeneration(id, {});
      navigate(`/generation/${result.generation_id}`);
    } catch {}
    setRegenerating(false);
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const result = await exportGeneration(id, { format: exportFormat, quality: exportQuality });
      window.open(result.download_url, '_blank');
      setShowExport(false);
    } catch {}
    setExporting(false);
  };

  if (loading) return <div className="gen-loading container">Loading...</div>;
  if (!gen) return null;

  return (
    <div className="gen container">
      <div className="gen-head">
        <div className="gen-breadcrumb">
          <span onClick={() => navigate('/dashboard')}>Projects</span>
          <span>/</span>
          <span onClick={() => navigate(`/project/${gen.project_id}`)}>Project</span>
          <span>/</span>
          <span>Generation</span>
        </div>
        <h2>Thumbnail Generation</h2>
      </div>

      <div className="gen-layout">
        <div className="gen-main">
          <Card className="gen-image-card">
            {gen.image_url ? (
              <img src={gen.image_url} alt="Thumbnail" className="gen-image" />
            ) : (
              <div className="gen-image-placeholder">
                {gen.status === 'generating' ? 'Generating your thumbnail...' : 'No image available'}
              </div>
            )}
            <div className="gen-prompt">
              <strong>Prompt:</strong> {gen.ai_prompt}
            </div>
          </Card>

          {gen.variants?.length > 0 && (
            <div className="gen-variants">
              <h3>Platform Variants</h3>
              <div className="gen-variants-grid">
                {gen.variants.map((v) => (
                  <Card key={v.id} className="gen-variant">
                    <img src={v.image_url} alt={v.platform} />
                    <Badge>{v.platform}</Badge>
                    <span className="gen-variant-size">{v.width}x{v.height}</span>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="gen-sidebar">
          <Card className="gen-actions-card">
            <h4>Actions</h4>
            <div className="gen-actions">
              <Button fullWidth onClick={handleRegenerate} loading={regenerating}>Regenerate</Button>
              <Button fullWidth variant="secondary" onClick={() => setShowExport(true)}>Export</Button>
              <Button fullWidth variant="accent2" onClick={handleScore} loading={scoring}>Score with AI</Button>
            </div>
          </Card>

          {gen.ai_score != null && (
            <Card className="gen-score-card">
              <h4>AI Score</h4>
              <div className="gen-score-visual">
                <div className="gen-score-number">{gen.ai_score}</div>
                <div className="gen-score-bar">
                  <div className="gen-score-fill" style={{ width: `${gen.ai_score}%` }} />
                </div>
              </div>
              {gen.ctr_prediction && (
                <div className="gen-ctr">
                  <span className="gen-ctr-label">CTR Potential</span>
                  <Badge variant={gen.ctr_prediction === 'viral' ? 'success' : gen.ctr_prediction === 'high' ? 'accent' : 'default'}>
                    {gen.ctr_prediction}
                  </Badge>
                </div>
              )}
              {gen.ai_feedback && (
                <div className="gen-feedback">
                  <strong>Feedback</strong>
                  <p>{gen.ai_feedback}</p>
                </div>
              )}
            </Card>
          )}

          <Card className="gen-meta-card">
            <h4>Details</h4>
            <div className="gen-meta-row">
              <span>Status</span>
              <Badge variant={gen.status === 'completed' ? 'success' : gen.status === 'generating' ? 'warning' : 'error'}>
                {gen.status}
              </Badge>
            </div>
            <div className="gen-meta-row">
              <span>Style</span>
              <span>{gen.style.replace(/_/g, ' ')}</span>
            </div>
            <div className="gen-meta-row">
              <span>Created</span>
              <span>{new Date(gen.created_at).toLocaleDateString()}</span>
            </div>
          </Card>
        </div>
      </div>

      <Modal open={showExport} onClose={() => setShowExport(false)} title="Export Thumbnail">
        <div className="gen-export-form">
          <div className="input-group">
            <label className="input-label">Format</label>
            <select className="input-field" value={exportFormat} onChange={(e) => setExportFormat(e.target.value)}>
              <option value="png">PNG</option>
              <option value="jpg">JPG</option>
              <option value="webp">WebP</option>
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">Quality ({exportQuality}%)</label>
            <input type="range" min={50} max={100} value={exportQuality} onChange={(e) => setExportQuality(Number(e.target.value))} className="gen-export-range" />
          </div>
          <Button fullWidth onClick={handleExport} loading={exporting}>Download</Button>
        </div>
      </Modal>
    </div>
  );
}
