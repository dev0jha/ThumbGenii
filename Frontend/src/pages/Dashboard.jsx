import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getProjects } from '../services/projects';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import './Dashboard.css';

const statusBadge = {
  draft: 'default',
  generating: 'warning',
  completed: 'success',
  failed: 'error',
};

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  const load = async (p = 1) => {
    setLoading(true);
    try {
      const data = await getProjects(p);
      setProjects(data.items);
      setTotal(data.total);
      setPage(data.page);
    } catch {
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="dashboard container">
      <div className="dashboard-head">
        <div>
          <h2>Your Projects</h2>
          <p className="dashboard-count">{total} project{total !== 1 ? 's' : ''}</p>
        </div>
        <Button onClick={() => navigate('/project/new')}>New Project</Button>
      </div>

      {loading ? (
        <div className="dashboard-empty">Loading...</div>
      ) : projects.length === 0 ? (
        <div className="dashboard-empty">
          <div className="dashboard-empty-icon">G</div>
          <h3>No projects yet</h3>
          <p>Create your first AI thumbnail project to get started.</p>
          <Button onClick={() => navigate('/project/new')}>Create Project</Button>
        </div>
      ) : (
        <div className="dashboard-grid">
          {projects.map((p) => (
            <Card key={p.id} hover onClick={() => navigate(`/project/${p.id}`)} className="dashboard-project">
              <div className="dashboard-project-top">
                <Badge variant={statusBadge[p.status] || 'default'}>{p.status}</Badge>
              </div>
              <h3 className="dashboard-project-title">{p.title}</h3>
              <p className="dashboard-project-prompt">{p.prompt}</p>
              <div className="dashboard-project-meta">
                <span>{p.style.replace(/_/g, ' ')}</span>
                <span>{new Date(p.created_at).toLocaleDateString()}</span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {total > 20 && (
        <div className="dashboard-pagination">
          <Button variant="secondary" size="sm" disabled={page <= 1} onClick={() => load(page - 1)}>Previous</Button>
          <span className="dashboard-page-info">Page {page} of {Math.ceil(total / 20)}</span>
          <Button variant="secondary" size="sm" disabled={page >= Math.ceil(total / 20)} onClick={() => load(page + 1)}>Next</Button>
        </div>
      )}
    </div>
  );
}
