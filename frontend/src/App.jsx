import React, { useState, useEffect } from 'react';
import {
  Search,
  UploadCloud,
  FileText,
  Shield,
  Tag,
  RefreshCw,
  Trash2,
  Edit3,
  CheckCircle,
  AlertCircle,
  BarChart2,
  Clock,
  Layers,
  Lock,
  User,
  X,
  Database,
  FileCheck,
  Server
} from 'lucide-react';

const API_BASE = 'http://localhost:8000/api/v1';

const PERSONAS = [
  { username: 'regular_user', role: 'user', label: 'Regular User', desc: 'Standard upload & search access' },
  { username: 'editor_user', role: 'editor', label: 'Content Editor', desc: 'Can correct AI metadata & taxonomy tags' },
  { username: 'admin_user', role: 'admin', label: 'Administrator', desc: 'Full taxonomy, re-indexing & metrics access' },
  { username: 'auditor_user', role: 'auditor', label: 'Auditor', desc: 'Compliance & audit log review only' },
];

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('search');
  const [notification, setNotification] = useState(null);
  const [categories, setCategories] = useState([]);

  // Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [searchCategory, setSearchCategory] = useState('');
  const [searchFileType, setSearchFileType] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchTotal, setSearchTotal] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Upload State
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);

  // Document Library & Metadata Inspection
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [activeDocMetadata, setActiveDocMetadata] = useState(null);
  const [inspectModalOpen, setInspectModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);

  // Metadata Edit Form State
  const [editCategory, setEditCategory] = useState('');
  const [editKeywords, setEditKeywords] = useState('');
  const [editTopics, setEditTopics] = useState('');
  const [editRevision, setEditRevision] = useState(1);
  const [isSavingMeta, setIsSavingMeta] = useState(false);
  const [conflictError, setConflictError] = useState(null);

  // Admin Console State
  const [adminMetrics, setAdminMetrics] = useState(null);
  const [newCatName, setNewCatName] = useState('');
  const [newCatDesc, setNewCatDesc] = useState('');
  const [isReindexing, setIsReindexing] = useState(false);
  const [reindexResult, setReindexResult] = useState(null);

  // Audit Logs State
  const [auditLogs, setAuditLogs] = useState([]);
  const [loadingAudit, setLoadingAudit] = useState(false);

  // Show toast notification
  const showNotification = (type, message) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  // Authenticate as a Persona
  const switchPersona = async (username) => {
    const pwdMap = {
      regular_user: 'UserPass123!',
      editor_user: 'EditorPass123!',
      admin_user: 'AdminPass123!',
      auditor_user: 'AuditorPass123!',
    };
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password: pwdMap[username] }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || 'Login failed');
      }
      const data = await res.json();
      const userObj = {
        username: data.username,
        role: data.role,
        token: data.access_token,
      };
      setCurrentUser(userObj);
      showNotification('success', `Logged in as ${username} (${data.role.toUpperCase()})`);
    } catch (err) {
      showNotification('error', `Authentication error: ${err.message}`);
    }
  };

  // Initial login on load
  useEffect(() => {
    switchPersona('regular_user');
  }, []);

  // Fetch Categories whenever user switches or on load
  const fetchCategories = async () => {
    if (!currentUser?.token) return;
    try {
      const res = await fetch(`${API_BASE}/categories`, {
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setCategories(data);
      }
    } catch (e) {
      console.error('Failed to load categories', e);
    }
  };

  useEffect(() => {
    if (currentUser) {
      fetchCategories();
      if (activeTab === 'explorer') loadDocuments();
      if (activeTab === 'admin' && currentUser.role === 'admin') loadAdminData();
      if (activeTab === 'audit' && (currentUser.role === 'admin' || currentUser.role === 'auditor')) loadAuditLogs();
    }
  }, [currentUser, activeTab]);

  // Execute Semantic Search
  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!currentUser?.token) return;
    setIsSearching(true);
    setHasSearched(true);
    try {
      const params = new URLSearchParams();
      if (searchQuery.trim()) params.append('q', searchQuery.trim());
      if (searchCategory) params.append('category', searchCategory);
      if (searchFileType) params.append('file_type', searchFileType);

      const res = await fetch(`${API_BASE}/search?${params.toString()}`, {
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || 'Search failed');
      }
      const data = await res.json();
      setSearchResults(data.results || []);
      setSearchTotal(data.total || 0);
    } catch (err) {
      showNotification('error', `Search error: ${err.message}`);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Handle Document Upload
  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile || !currentUser?.token) return;

    if (selectedFile.size > 20 * 1024 * 1024) {
      showNotification('error', 'File size exceeds maximum 20MB limit (AICMS-F-002)');
      return;
    }

    setIsUploading(true);
    setUploadProgress('Ingesting and verifying document integrity...');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${currentUser.token}` },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        if (res.status === 409) {
          throw new Error(`Duplicate File Conflict: ${err.message}`);
        } else if (res.status === 413) {
          throw new Error(`Payload Too Large: ${err.message}`);
        }
        throw new Error(err.message || 'Upload failed');
      }

      const data = await res.json();
      showNotification('success', `Uploaded "${data.title}" successfully! Status: ${data.status}`);
      setSelectedFile(null);
      setUploadProgress(null);
      // Automatically refresh documents list if explorer is visited
      loadDocuments();
    } catch (err) {
      showNotification('error', err.message);
      setUploadProgress(null);
    } finally {
      setIsUploading(false);
    }
  };

  // Load Document Explorer
  const loadDocuments = async () => {
    if (!currentUser?.token) return;
    setLoadingDocs(true);
    try {
      const res = await fetch(`${API_BASE}/documents?limit=50`, {
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (e) {
      showNotification('error', 'Failed to retrieve documents');
    } finally {
      setLoadingDocs(false);
    }
  };

  // Inspect Document Metadata
  const openInspectModal = async (docId) => {
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}/metadata`, {
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || 'Could not fetch metadata');
      }
      const data = await res.json();
      setActiveDocMetadata(data);
      setInspectModalOpen(true);
    } catch (err) {
      showNotification('error', err.message);
    }
  };

  // Open Edit Metadata Modal
  const openEditModal = async (docId) => {
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}/metadata`, {
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || 'Could not fetch metadata');
      }
      const data = await res.json();
      setActiveDocMetadata(data);
      setEditCategory(data.category_name || '');
      setEditKeywords((data.keywords || []).join(', '));
      setEditTopics((data.topics || []).join(', '));
      setEditRevision(data.revision);
      setConflictError(null);
      setEditModalOpen(true);
    } catch (err) {
      showNotification('error', err.message);
    }
  };

  // Save Metadata Changes (Optimistic Concurrency)
  const handleSaveMetadata = async (e) => {
    e.preventDefault();
    if (!activeDocMetadata || !currentUser?.token) return;
    setIsSavingMeta(true);
    setConflictError(null);

    const kwArray = editKeywords.split(',').map((s) => s.trim()).filter(Boolean);
    const topArray = editTopics.split(',').map((s) => s.trim()).filter(Boolean);

    try {
      const res = await fetch(`${API_BASE}/documents/${activeDocMetadata.document_id}/metadata`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${currentUser.token}`,
        },
        body: JSON.stringify({
          category_name: editCategory || null,
          keywords: kwArray,
          topics: topArray,
          revision: editRevision,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        if (res.status === 409) {
          setConflictError(err.message || 'Concurrency conflict: revision mismatch!');
          throw new Error('Concurrency Conflict: Another user has modified this metadata.');
        } else if (res.status === 403) {
          throw new Error('Permission Denied: Only content editors or admins can edit metadata.');
        }
        throw new Error(err.message || 'Update failed');
      }

      const updated = await res.json();
      showNotification('success', `Metadata updated! New revision is ${updated.revision}.`);
      setActiveDocMetadata(updated);
      setEditModalOpen(false);
      loadDocuments();
    } catch (err) {
      showNotification('error', err.message);
    } finally {
      setIsSavingMeta(false);
    }
  };

  // Delete Document and Purge Vectors
  const handleDeleteDoc = async (docId, title) => {
    if (!window.confirm(`Are you sure you want to delete and purge "${title}"? This cannot be undone.`)) return;
    try {
      const res = await fetch(`${API_BASE}/documents/${docId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || 'Deletion failed');
      }
      showNotification('success', `Document "${title}" and associated vectors purged successfully.`);
      loadDocuments();
    } catch (err) {
      showNotification('error', err.message);
    }
  };

  // Admin: Load Metrics & Taxonomy
  const loadAdminData = async () => {
    if (!currentUser?.token || currentUser.role !== 'admin') return;
    try {
      const resM = await fetch(`${API_BASE}/admin/metrics`, {
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (resM.ok) {
        setAdminMetrics(await resM.json());
      }
      fetchCategories();
    } catch (e) {
      console.error(e);
    }
  };

  // Admin: Create Category
  const handleCreateCategory = async (e) => {
    e.preventDefault();
    if (!newCatName.trim() || currentUser.role !== 'admin') return;
    try {
      const res = await fetch(`${API_BASE}/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${currentUser.token}`,
        },
        body: JSON.stringify({ name: newCatName.trim(), description: newCatDesc.trim() || null }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || 'Category creation failed');
      }
      showNotification('success', `Category "${newCatName.trim()}" added to taxonomy.`);
      setNewCatName('');
      setNewCatDesc('');
      fetchCategories();
    } catch (err) {
      showNotification('error', err.message);
    }
  };

  // Admin: Delete Category with Referential Integrity check
  const handleDeleteCategory = async (catId, catName) => {
    if (!window.confirm(`Delete category "${catName}"?`)) return;
    try {
      const res = await fetch(`${API_BASE}/categories/${catId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || 'Category deletion failed');
      }
      showNotification('success', `Category "${catName}" deleted.`);
      fetchCategories();
    } catch (err) {
      showNotification('error', err.message);
    }
  };

  // Admin: Trigger Semantic Re-indexing
  const handleTriggerReindex = async () => {
    if (currentUser.role !== 'admin') return;
    setIsReindexing(true);
    setReindexResult(null);
    try {
      const res = await fetch(`${API_BASE}/admin/reindex`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${currentUser.token}`,
        },
        body: JSON.stringify({ force: true }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.message || 'Re-index trigger failed');
      }
      const data = await res.json();
      setReindexResult(data);
      showNotification('success', `Re-index job completed! ${data.documents_queued} docs re-indexed.`);
    } catch (err) {
      showNotification('error', err.message);
    } finally {
      setIsReindexing(false);
    }
  };

  // Auditor: Load Audit Logs
  const loadAuditLogs = async () => {
    if (!currentUser?.token) return;
    setLoadingAudit(true);
    try {
      const res = await fetch(`${API_BASE}/audit/logs?limit=50`, {
        headers: { Authorization: `Bearer ${currentUser.token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setAuditLogs(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingAudit(false);
    }
  };

  // Category Color Badge Helper
  const getCategoryBadgeClass = (category) => {
    switch (category) {
      case 'Engineering':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'Finance':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'Legal':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'Human Resources':
        return 'bg-purple-500/20 text-purple-300 border-purple-500/30';
      case 'Operations':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      default:
        return 'bg-slate-500/20 text-slate-300 border-slate-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Toast Notification */}
      {notification && (
        <div
          role="status"
          aria-live="polite"
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-2xl border flex items-center space-x-3 transition-all ${
            notification.type === 'error'
              ? 'bg-rose-950/90 text-rose-200 border-rose-800'
              : 'bg-emerald-950/90 text-emerald-200 border-emerald-800'
          }`}
        >
          {notification.type === 'error' ? <AlertCircle className="w-5 h-5 text-rose-400" /> : <CheckCircle className="w-5 h-5 text-emerald-400" />}
          <span className="text-sm font-medium">{notification.message}</span>
          <button
            onClick={() => setNotification(null)}
            className="p-1 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white"
            aria-label="Close notification"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Top Navigation & Persona Bar */}
      <header className="border-b border-slate-800 bg-slate-900/90 sticky top-0 z-40 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-indigo-400 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
                AI
              </div>
              <div>
                <span className="font-bold text-lg tracking-tight text-white">AICMS</span>
                <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  v1.0-freeze
                </span>
              </div>
            </div>

            {/* Persona Switcher Buttons (TC-ADM-03, TC-SEC-01) */}
            <div className="flex items-center space-x-2 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 px-2 flex items-center space-x-1">
                <User className="w-3.5 h-3.5 text-slate-500" />
                <span className="hidden md:inline">Persona:</span>
              </span>
              {PERSONAS.map((p) => {
                const isActive = currentUser?.username === p.username;
                return (
                  <button
                    key={p.username}
                    onClick={() => switchPersona(p.username)}
                    className={`px-2.5 py-1 text-xs rounded-lg font-medium transition focus:ring-2 focus:ring-indigo-500 focus:outline-none ${
                      isActive
                        ? 'bg-indigo-600 text-white shadow'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                    title={p.desc}
                    aria-label={`Switch persona to ${p.label}`}
                  >
                    {p.label.split(' ')[0]}
                    <span className="ml-1 opacity-70 text-[10px]">({p.role})</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Sub Navigation Tabs */}
          <nav className="flex space-x-1 border-t border-slate-800/60 pt-1 pb-2 overflow-x-auto" aria-label="Main Navigation">
            <button
              onClick={() => setActiveTab('search')}
              className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center space-x-2 transition focus:ring-2 focus:ring-indigo-500 focus:outline-none ${
                activeTab === 'search' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <Search className="w-4 h-4 text-indigo-400" />
              <span>Semantic Search</span>
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center space-x-2 transition focus:ring-2 focus:ring-indigo-500 focus:outline-none ${
                activeTab === 'upload' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <UploadCloud className="w-4 h-4 text-emerald-400" />
              <span>Intake & Upload</span>
            </button>
            <button
              onClick={() => setActiveTab('explorer')}
              className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center space-x-2 transition focus:ring-2 focus:ring-indigo-500 focus:outline-none ${
                activeTab === 'explorer' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <FileText className="w-4 h-4 text-blue-400" />
              <span>Document Explorer</span>
            </button>
            {currentUser?.role === 'admin' && (
              <button
                onClick={() => setActiveTab('admin')}
                className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center space-x-2 transition focus:ring-2 focus:ring-indigo-500 focus:outline-none ${
                  activeTab === 'admin' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Server className="w-4 h-4 text-amber-400" />
                <span>Admin & Taxonomy</span>
              </button>
            )}
            {(currentUser?.role === 'admin' || currentUser?.role === 'auditor') && (
              <button
                onClick={() => setActiveTab('audit')}
                className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center space-x-2 transition focus:ring-2 focus:ring-indigo-500 focus:outline-none ${
                  activeTab === 'audit' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Shield className="w-4 h-4 text-rose-400" />
                <span>Audit Logs</span>
              </button>
            )}
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {/* ======================================================== */}
        {/* TAB 1: SEMANTIC SEARCH (AICMS-F-011..015, TC-SR-01..04)   */}
        {/* ======================================================== */}
        {activeTab === 'search' && (
          <div className="space-y-6">
            {/* Search Header Form */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <Search className="w-5 h-5 text-indigo-400" />
                <span>Natural-Language Semantic Retrieval</span>
              </h2>
              <p className="text-sm text-slate-400">
                Vector similarity search powered by 384-dimensional embeddings and PostgreSQL pgvector cosine distance.
              </p>

              <form onSubmit={handleSearch} className="space-y-4">
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Enter natural language query (e.g., 'how to configure microservices architecture')"
                    className="w-full pl-11 pr-28 py-3.5 bg-slate-950 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 text-base focus:ring-2 focus:ring-indigo-500 focus:outline-none transition shadow-inner"
                    aria-label="Semantic search query"
                  />
                  <Search className="w-5 h-5 text-slate-500 absolute left-4 top-4" />
                  <button
                    type="submit"
                    disabled={isSearching}
                    className="absolute right-2 top-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg transition focus:ring-2 focus:ring-indigo-400 focus:outline-none disabled:opacity-50"
                  >
                    {isSearching ? 'Searching...' : 'Search'}
                  </button>
                </div>

                {/* Filter Pills */}
                <div className="flex flex-wrap items-center gap-3 pt-1 text-xs">
                  <span className="text-slate-400 font-medium">Filters:</span>
                  <select
                    value={searchCategory}
                    onChange={(e) => setSearchCategory(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    aria-label="Filter by category"
                  >
                    <option value="">All Categories</option>
                    {categories.map((c) => (
                      <option key={c.id} value={c.name}>
                        {c.name}
                      </option>
                    ))}
                  </select>

                  <select
                    value={searchFileType}
                    onChange={(e) => setSearchFileType(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    aria-label="Filter by file type"
                  >
                    <option value="">All File Types</option>
                    <option value="pdf">PDF</option>
                    <option value="docx">DOCX</option>
                    <option value="txt">TXT</option>
                  </select>

                  {(searchCategory || searchFileType || searchQuery) && (
                    <button
                      type="button"
                      onClick={() => {
                        setSearchQuery('');
                        setSearchCategory('');
                        setSearchFileType('');
                        setSearchResults([]);
                        setHasSearched(false);
                      }}
                      className="text-slate-400 hover:text-slate-200 text-xs underline"
                    >
                      Clear Filters
                    </button>
                  )}
                </div>
              </form>
            </div>

            {/* Results Section */}
            {hasSearched && (
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm text-slate-400">
                  <span>Found {searchTotal} authorized document{searchTotal === 1 ? '' : 's'}</span>
                  <span className="text-xs text-slate-500">Ordered by dense cosine similarity</span>
                </div>

                {searchResults.length === 0 ? (
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 text-center space-y-2">
                    <AlertCircle className="w-8 h-8 text-slate-500 mx-auto" />
                    <h3 className="text-base font-semibold text-slate-200">No Authorized Documents Found</h3>
                    <p className="text-sm text-slate-400 max-w-md mx-auto">
                      No matching records met your search criteria and permission policies. Try broader keywords or switch personas.
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-4">
                    {searchResults.map((res) => {
                      const simPct = Math.round(res.similarity_score * 100);
                      return (
                        <div
                          key={res.document_id}
                          className="bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-xl p-5 shadow transition space-y-3"
                        >
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <div className="flex items-center space-x-2">
                                <h3 className="text-lg font-semibold text-white hover:text-indigo-400 transition cursor-pointer" onClick={() => openInspectModal(res.document_id)}>
                                  {res.title}
                                </h3>
                                <span className={`text-[11px] font-medium px-2.5 py-0.5 rounded-full border ${getCategoryBadgeClass(res.category_name)}`}>
                                  {res.category_name || 'Uncategorized'}
                                </span>
                                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                                  {res.file_type}
                                </span>
                              </div>
                            </div>

                            {/* Cosine Similarity Score Badge */}
                            <div className="flex items-center space-x-1.5 bg-indigo-950/60 border border-indigo-700/40 px-3 py-1 rounded-lg">
                              <span className="text-xs text-indigo-300">Relevance:</span>
                              <strong className="text-sm text-indigo-200">{simPct}%</strong>
                            </div>
                          </div>

                          {/* Contextual Snippet */}
                          <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                            {res.snippet}
                          </p>

                          {/* Keywords & Actions */}
                          <div className="flex items-center justify-between pt-1">
                            <div className="flex flex-wrap items-center gap-1.5">
                              {(res.keywords || []).slice(0, 5).map((kw, i) => (
                                <span key={i} className="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-md flex items-center space-x-1">
                                  <Tag className="w-3 h-3 text-slate-500" />
                                  <span>{kw}</span>
                                </span>
                              ))}
                            </div>

                            <button
                              onClick={() => openInspectModal(res.document_id)}
                              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium underline focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                            >
                              Inspect Full Metadata &rarr;
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 2: INTAKE & UPLOAD (AICMS-F-001..004, TC-UP-01..04)  */}
        {/* ======================================================== */}
        {activeTab === 'upload' && (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <UploadCloud className="w-5 h-5 text-emerald-400" />
                <span>Multi-Format Document Intake</span>
              </h2>
              <p className="text-sm text-slate-400">
                Upload documents to trigger automated validation, SHA-256 deduplication, native metadata extraction, and vector embedding.
              </p>

              <form onSubmit={handleUpload} className="space-y-5">
                <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-2xl p-8 text-center transition bg-slate-950/40 space-y-3">
                  <input
                    type="file"
                    id="file-upload"
                    accept=".pdf,.docx,.txt"
                    onChange={(e) => setSelectedFile(e.target.files[0] || null)}
                    className="hidden"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer space-y-2 block focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-xl p-2">
                    <UploadCloud className="w-12 h-12 text-indigo-400 mx-auto animate-bounce" />
                    <div className="text-sm font-medium text-white">
                      {selectedFile ? (
                        <span className="text-emerald-400 font-semibold">{selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                      ) : (
                        <span>Click to browse or drop document here</span>
                      )}
                    </div>
                    <p className="text-xs text-slate-500">Supported formats: PDF, DOCX, TXT (Maximum limit: 20MB)</p>
                  </label>
                </div>

                {uploadProgress && (
                  <div className="flex items-center space-x-2 text-sm text-indigo-300 bg-indigo-950/40 p-3 rounded-lg border border-indigo-800">
                    <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
                    <span>{uploadProgress}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!selectedFile || isUploading}
                  className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-xl transition shadow-lg shadow-emerald-600/20 disabled:opacity-50 focus:ring-2 focus:ring-emerald-400 focus:outline-none"
                >
                  {isUploading ? 'Ingesting Document...' : 'Ingest Document'}
                </button>
              </form>
            </div>

            {/* Ingestion Rules Card */}
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 space-y-3 text-xs text-slate-400">
              <h4 className="font-semibold text-slate-200 uppercase tracking-wider">Automated Intake Pipeline Gates</h4>
              <ul className="space-y-1.5 list-disc list-inside">
                <li>Magic byte verification protects against disguised executables (TC-SEC-04).</li>
                <li>SHA-256 duplicate detection rejects redundant content with HTTP 409 (TC-UP-03).</li>
                <li>Asynchronous worker extracts text and categorizes into approved taxonomy (TC-AI-02).</li>
              </ul>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 3: EXPLORER & METADATA EDITOR (TC-MD-01, TC-DATA-01) */}
        {/* ======================================================== */}
        {activeTab === 'explorer' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <span>Authorized Document Library</span>
                </h2>
                <p className="text-sm text-slate-400">
                  Manage documents, inspect AI classification confidence, and edit metadata with optimistic concurrency.
                </p>
              </div>
              <button
                onClick={loadDocuments}
                className="px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-lg text-xs font-medium text-slate-200 transition flex items-center space-x-1.5"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingDocs ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>

            {loadingDocs ? (
              <div className="text-center py-12 text-slate-400">Loading documents...</div>
            ) : documents.length === 0 ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 text-center space-y-2">
                <FileCheck className="w-8 h-8 text-slate-500 mx-auto" />
                <h3 className="text-base font-semibold text-slate-200">No Accessible Documents</h3>
                <p className="text-sm text-slate-400 max-w-sm mx-auto">
                  No documents found for this user persona. Upload a document or switch to an administrator account.
                </p>
              </div>
            ) : (
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-950 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="px-5 py-3.5">ID</th>
                      <th className="px-5 py-3.5">Title</th>
                      <th className="px-5 py-3.5">Format</th>
                      <th className="px-5 py-3.5">Size</th>
                      <th className="px-5 py-3.5">Status</th>
                      <th className="px-5 py-3.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/80">
                    {documents.map((doc) => (
                      <tr key={doc.id} className="hover:bg-slate-800/40 transition">
                        <td className="px-5 py-3 font-mono text-xs text-slate-400">{doc.id}</td>
                        <td className="px-5 py-3 font-medium text-white">{doc.title}</td>
                        <td className="px-5 py-3 text-xs uppercase text-slate-400">{doc.file_type}</td>
                        <td className="px-5 py-3 text-xs text-slate-400">{(doc.file_size / 1024).toFixed(1)} KB</td>
                        <td className="px-5 py-3">
                          <span
                            className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                              doc.status === 'COMPLETED'
                                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                : doc.status === 'FAILED'
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : 'bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse'
                            }`}
                          >
                            {doc.status}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-right space-x-2">
                          <button
                            onClick={() => openInspectModal(doc.id)}
                            className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-medium transition"
                          >
                            Inspect
                          </button>
                          {(currentUser.role === 'editor' || currentUser.role === 'admin') && (
                            <button
                              onClick={() => openEditModal(doc.id)}
                              className="px-2.5 py-1 text-xs bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 rounded font-medium transition"
                            >
                              Edit
                            </button>
                          )}
                          {(currentUser.role === 'admin' || doc.owner_id === currentUser.id) && (
                            <button
                              onClick={() => handleDeleteDoc(doc.id, doc.title)}
                              className="px-2.5 py-1 text-xs bg-rose-600/20 hover:bg-rose-600/40 text-rose-300 border border-rose-500/30 rounded font-medium transition"
                            >
                              Purge
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 4: ADMIN & TAXONOMY CONSOLE (TC-ADM-01, TC-OPS-02)   */}
        {/* ======================================================== */}
        {activeTab === 'admin' && currentUser.role === 'admin' && (
          <div className="space-y-8">
            {/* Operational Metrics Cards (AICMS-F-022, TC-OPS-02, TC-OPS-03) */}
            <div className="space-y-3">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <BarChart2 className="w-5 h-5 text-indigo-400" />
                <span>Operational Health & Availability Metrics</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Service Uptime</div>
                  <div className="text-2xl font-bold text-white">
                    {adminMetrics ? `${adminMetrics.uptime_seconds}s` : '---'}
                  </div>
                  <div className="text-xs text-slate-500">Live process elapsed time</div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Availability SLA</div>
                  <div className="text-2xl font-bold text-emerald-400">
                    {adminMetrics ? `${adminMetrics.availability_percentage}%` : '---'}
                  </div>
                  <div className="text-xs text-slate-500">Target &ge; 99.5% (AICMS-NF-002)</div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Uploads Handled</div>
                  <div className="text-2xl font-bold text-blue-400">
                    {adminMetrics ? `${adminMetrics.uploads.successful} / ${adminMetrics.uploads.total}` : '---'}
                  </div>
                  <div className="text-xs text-slate-500">Successful vs Total</div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs text-slate-400 uppercase font-semibold">Search p90 Latency</div>
                  <div className="text-2xl font-bold text-purple-400">
                    {adminMetrics ? `${adminMetrics.search.p90_latency_ms} ms` : '---'}
                  </div>
                  <div className="text-xs text-slate-500">Under 3000ms SLA target</div>
                </div>
              </div>
            </div>

            {/* Taxonomy Categories Management (TC-ADM-01) */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <Tag className="w-5 h-5 text-emerald-400" />
                <span>Approved Category Taxonomy (AICMS-F-019)</span>
              </h3>
              <p className="text-xs text-slate-400">
                Categories define the multi-class document classification space. Referential integrity prevents deleting categories that have active document bindings.
              </p>

              {/* Add Category Form */}
              <form onSubmit={handleCreateCategory} className="flex flex-wrap items-center gap-3 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <input
                  type="text"
                  placeholder="New Category Name (e.g., Compliance)"
                  value={newCatName}
                  onChange={(e) => setNewCatName(e.target.value)}
                  className="px-3.5 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  aria-label="New category name"
                />
                <input
                  type="text"
                  placeholder="Description (optional)"
                  value={newCatDesc}
                  onChange={(e) => setNewCatDesc(e.target.value)}
                  className="flex-1 min-w-[200px] px-3.5 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  aria-label="New category description"
                />
                <button
                  type="submit"
                  disabled={!newCatName.trim()}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-lg transition disabled:opacity-50 focus:ring-2 focus:ring-emerald-400 focus:outline-none"
                >
                  Add Category
                </button>
              </form>

              {/* Categories Table */}
              <div className="border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-950 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="px-4 py-3">Category Name</th>
                      <th className="px-4 py-3">Description</th>
                      <th className="px-4 py-3">Bound Documents</th>
                      <th className="px-4 py-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {categories.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-800/30">
                        <td className="px-4 py-3 font-semibold text-white">{c.name}</td>
                        <td className="px-4 py-3 text-slate-400 text-xs">{c.description || 'No description'}</td>
                        <td className="px-4 py-3">
                          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                            {c.document_count} doc{c.document_count === 1 ? '' : 's'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => handleDeleteCategory(c.id, c.name)}
                            className="px-2.5 py-1 text-xs text-rose-400 hover:text-rose-200 hover:bg-rose-950/40 rounded transition"
                            title={c.document_count > 0 ? 'Cannot delete category with bound documents' : 'Delete category'}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Semantic Re-indexing Trigger (AICMS-F-020, TC-ADM-02) */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <RefreshCw className="w-5 h-5 text-amber-400" />
                <span>Trigger Dense Vector Re-indexing (TC-ADM-02)</span>
              </h3>
              <p className="text-xs text-slate-400 max-w-xl">
                Queues a background job to re-compute all-MiniLM-L6-v2 embeddings for all completed documents after model configuration or taxonomy profile updates.
              </p>

              <div className="flex items-center space-x-4">
                <button
                  onClick={handleTriggerReindex}
                  disabled={isReindexing}
                  className="px-5 py-2.5 bg-amber-600 hover:bg-amber-500 text-white font-medium text-sm rounded-xl transition disabled:opacity-50 shadow-lg shadow-amber-600/20 focus:ring-2 focus:ring-amber-400 focus:outline-none flex items-center space-x-2"
                >
                  <RefreshCw className={`w-4 h-4 ${isReindexing ? 'animate-spin' : ''}`} />
                  <span>{isReindexing ? 'Re-indexing Documents...' : 'Execute Re-index Job'}</span>
                </button>

                {reindexResult && (
                  <div className="text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/60 p-2.5 rounded-lg">
                    Job ID: <strong className="font-mono">{reindexResult.job_id}</strong> &bull; Status: {reindexResult.status} &bull; Documents: {reindexResult.documents_queued}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 5: AUDIT LOGS (AICMS-F-018, TC-SEC-02)                */}
        {/* ======================================================== */}
        {activeTab === 'audit' && (currentUser.role === 'admin' || currentUser.role === 'auditor') && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-rose-400" />
                  <span>Tamper-Evident Security Audit Trail</span>
                </h2>
                <p className="text-sm text-slate-400">
                  Searchable log of authentication, document mutations, metadata corrections, and administrative actions without secrets.
                </p>
              </div>
              <button
                onClick={loadAuditLogs}
                className="px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded-lg text-xs font-medium text-slate-200 transition flex items-center space-x-1.5"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingAudit ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3">Timestamp</th>
                    <th className="px-4 py-3">Event Type</th>
                    <th className="px-4 py-3">User</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-xs">
                  {auditLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/40">
                      <td className="px-4 py-2.5 font-mono text-slate-400">{new Date(log.created_at).toLocaleTimeString()}</td>
                      <td className="px-4 py-2.5 font-semibold text-indigo-300">{log.event_type}</td>
                      <td className="px-4 py-2.5 text-slate-200">{log.username || 'System'}</td>
                      <td className="px-4 py-2.5">
                        <span
                          className={`px-2 py-0.5 rounded font-bold uppercase text-[10px] ${
                            log.status === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                          }`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-slate-400 max-w-md truncate" title={log.details}>
                        {log.details || '---'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* ======================================================== */}
      {/* MODAL 1: METADATA INSPECTOR MODAL                        */}
      {/* ======================================================== */}
      {inspectModalOpen && activeDocMetadata && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <FileText className="w-5 h-5 text-indigo-400" />
                <span>Document Metadata & AI Extraction</span>
              </h3>
              <button onClick={() => setInspectModalOpen(false)} className="text-slate-400 hover:text-white" aria-label="Close modal">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-1 text-sm">
              <div className="grid grid-cols-2 gap-3 text-xs bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-400">Title:</span> <strong className="text-white block">{activeDocMetadata.title}</strong>
                </div>
                <div>
                  <span className="text-slate-400">Category:</span>{' '}
                  <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-semibold border ${getCategoryBadgeClass(activeDocMetadata.category_name)}`}>
                    {activeDocMetadata.category_name}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Confidence Score:</span>{' '}
                  <strong className="text-emerald-400 block">{Math.round((activeDocMetadata.category_confidence || 0) * 100)}%</strong>
                </div>
                <div>
                  <span className="text-slate-400">Revision Number:</span> <strong className="text-indigo-400 block">{activeDocMetadata.revision}</strong>
                </div>
                <div>
                  <span className="text-slate-400">Word Count:</span> <span className="text-slate-200 block">{activeDocMetadata.word_count} words</span>
                </div>
                <div>
                  <span className="text-slate-400">Embedding Model:</span> <span className="text-slate-200 block">{activeDocMetadata.embedding_model} ({activeDocMetadata.model_version})</span>
                </div>
              </div>

              {/* Keywords & Topics */}
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-slate-400 uppercase">Extracted Keywords:</span>
                <div className="flex flex-wrap gap-1.5">
                  {(activeDocMetadata.keywords || []).map((kw, i) => (
                    <span key={i} className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              {/* Extracted Text Preview */}
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-slate-400 uppercase">Extracted Text Content:</span>
                <div className="bg-slate-950 border border-slate-800 p-3.5 rounded-xl text-xs text-slate-300 font-mono leading-relaxed max-h-48 overflow-y-auto">
                  {activeDocMetadata.extracted_text}
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <button
                onClick={() => setInspectModalOpen(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* MODAL 2: METADATA EDITOR MODAL (TC-MD-01)                 */}
      {/* ======================================================== */}
      {editModalOpen && activeDocMetadata && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <Edit3 className="w-5 h-5 text-indigo-400" />
                <span>Correct AI Metadata (TC-MD-01)</span>
              </h3>
              <button onClick={() => setEditModalOpen(false)} className="text-slate-400 hover:text-white" aria-label="Close edit modal">
                <X className="w-5 h-5" />
              </button>
            </div>

            {conflictError && (
              <div className="bg-rose-950/80 border border-rose-800 p-3 rounded-xl text-xs text-rose-200 flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{conflictError}</span>
              </div>
            )}

            <form onSubmit={handleSaveMetadata} className="space-y-4 text-sm">
              <div className="text-xs text-slate-400 bg-slate-950 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                <span>Document: <strong className="text-white">{activeDocMetadata.title}</strong></span>
                <span>Optimistic Revision: <strong className="text-indigo-400 font-mono">{editRevision}</strong></span>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                  Taxonomy Category:
                </label>
                <select
                  value={editCategory}
                  onChange={(e) => setEditCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.name}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                  Keywords (comma-separated):
                </label>
                <input
                  type="text"
                  value={editKeywords}
                  onChange={(e) => setEditKeywords(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  placeholder="e.g. microservices, kubernetes, docker"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">
                  Topic Descriptors (comma-separated):
                </label>
                <input
                  type="text"
                  value={editTopics}
                  onChange={(e) => setEditTopics(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  placeholder="e.g. Cloud Infrastructure, Container Orchestration"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setEditModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSavingMeta}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium rounded-lg transition shadow-lg shadow-indigo-600/30 disabled:opacity-50"
                >
                  {isSavingMeta ? 'Saving Changes...' : 'Save Revisions'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500">
        AICMS &bull; Software Engineering Mini-Project &bull; PES University &bull; Phase 2 & 3 Deliverable
      </footer>
    </div>
  );
}
