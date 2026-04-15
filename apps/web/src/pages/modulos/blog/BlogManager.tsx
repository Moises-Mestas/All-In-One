// apps/web/src/pages/modulos/blog/BlogManager.tsx
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { blogService } from "../../../services/blog.service";
import ReactQuill from "react-quill-new";
import "react-quill-new/dist/quill.snow.css";

export default function BlogManager() {
  const { siteId } = useParams();
  const navigate = useNavigate();
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  // 📝 ESTADOS DEL FORMULARIO
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [excerpt, setExcerpt] = useState(""); 
  const [featuredImage, setFeaturedImage] = useState(""); 
  const [metaTitle, setMetaTitle] = useState(""); 
  const [metaDescription, setMetaDescription] = useState(""); 
  const [status, setStatus] = useState("draft");
  
  // 👇 NUEVO: Estado para saber si estamos editando un post existente
  const [editingPostId, setEditingPostId] = useState<number | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [publishedAt, setPublishedAt] = useState("");

  const loadPosts = async () => {
    if (!siteId) return;
    try {
      const data = await blogService.getPosts(Number(siteId));
      setPosts(data);
    } catch (err) {
      console.error("Error al cargar posts", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadPosts(); }, [siteId]);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !siteId) return;
    
    setIsUploading(true);
    try {
      const imageUrl = await blogService.uploadImage(Number(siteId), file);
      setFeaturedImage(imageUrl); 
    } catch (error) {
      console.error("Error al subir", error);
      alert("Error al subir la imagen. Verifica que el backend esté configurado.");
    } finally {
      setIsUploading(false);
    }
  };

  // 👇 NUEVO: Función para cargar los datos de un post en el formulario
  const handleEdit = (post: any) => {
      setEditingPostId(post.id);
      setTitle(post.title || "");
      setContent(post.content || "");
      setExcerpt(post.excerpt || "");
      setFeaturedImage(post.featured_image || "");
      setMetaTitle(post.meta_title || "");
      setMetaDescription(post.meta_description || "");
      setStatus(post.status || "draft");
      
      // 👇 NUEVO: Formateamos la fecha del backend para que el input HTML la entienda
      if (post.published_at) {
        const date = new Date(post.published_at);
        const localFormat = new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        setPublishedAt(localFormat);
      } else {
        setPublishedAt("");
      }
      
      window.scrollTo({ top: 0, behavior: "smooth" });
    };

  const handleCancelEdit = () => {
      setEditingPostId(null);
      setTitle(""); setContent(""); setExcerpt(""); 
      setFeaturedImage(""); setMetaTitle(""); setMetaDescription(""); 
      setStatus("draft");
      setPublishedAt(""); 
    };
  // 👇 MODIFICADO: Ahora detecta si guarda uno nuevo o actualiza uno existente
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!siteId) return;
    try {
      const postData = { 
        title, 
        content, 
        excerpt,
        featured_image: featuredImage,
        meta_title: metaTitle,
        meta_description: metaDescription,
        status,
        published_at: status === "scheduled" && publishedAt ? new Date(publishedAt).toISOString() : null
      };

      if (editingPostId) {
        // Modo Edición
        await blogService.updatePost(Number(siteId), editingPostId, postData);
        alert("¡Artículo actualizado exitosamente!");
      } else {
        // Modo Creación
        await blogService.createPost(Number(siteId), postData);
        alert("¡Artículo creado exitosamente!");
      }
      
      handleCancelEdit(); // Limpiamos el formulario
      loadPosts(); // Recargamos la lista
    } catch (err) {
      console.error("Error al guardar post", err);
      alert("Hubo un error al guardar el artículo.");
    }
  };

  const handleDelete = async (postId: number) => {
    if (!siteId || !confirm("¿Seguro que deseas eliminar este artículo?")) return;
    try {
      await blogService.deletePost(Number(siteId), postId);
      // Si estamos editando el post que justo acabamos de borrar, limpiamos el formulario
      if (editingPostId === postId) {
        handleCancelEdit();
      }
      loadPosts();
    } catch (error) {
      console.error("Error eliminando", error);
    }
  };

  const inputStyle = { width: "100%", padding: "10px", background: "#2a2a2a", color: "#fff", border: "1px solid #444", borderRadius: "6px", boxSizing: "border-box" as const, marginBottom: "15px" };
  const labelStyle = { display: "block", marginBottom: "5px", fontSize: "14px", color: "#bbb", fontWeight: "bold" as const };

  return (
    <div style={{ padding: "30px", background: "#111", minHeight: "100vh", color: "white", fontFamily: "sans-serif" }}>
      <button onClick={() => navigate(-1)} style={{ padding: "8px 15px", background: "#333", color: "white", border: "none", borderRadius: "4px", marginBottom: "20px", cursor: "pointer" }}>⬅ Volver</button>
      
      {/* Título dinámico dependiendo si editamos o creamos */}
      <h1 style={{ marginTop: 0, borderBottom: "1px solid #333", paddingBottom: "15px", color: editingPostId ? "#f59e0b" : "white" }}>
        {editingPostId ? "✏️ Editando Artículo" : "📝 Panel Editorial del Blog"}
      </h1>
      
      <form onSubmit={handleSave} style={{ display: "flex", gap: "30px", marginTop: "20px", flexWrap: "wrap" }}>
        
        {/* COLUMNA IZQUIERDA: CONTENIDO PRINCIPAL */}
        <div style={{ flex: "2", minWidth: "400px", display: "flex", flexDirection: "column", gap: "20px" }}>
          <div style={{ background: "#1e1e1e", padding: "25px", borderRadius: "8px", border: "1px solid #333", position: "relative" }}>
            
            {/* Indicador visual de modo edición */}
            {editingPostId && (
              <div style={{ position: "absolute", top: 0, right: 0, background: "#f59e0b", color: "#000", padding: "5px 15px", borderBottomLeftRadius: "8px", borderTopRightRadius: "8px", fontWeight: "bold", fontSize: "12px" }}>
                MODO EDICIÓN
              </div>
            )}

            <label style={labelStyle}>Título del Artículo *</label>
            <input 
              type="text" 
              placeholder="Ej: Las 10 nuevas tendencias del 2026..." 
              value={title} 
              onChange={(e) => setTitle(e.target.value)}
              style={{ ...inputStyle, fontSize: "18px", fontWeight: "bold" }}
              required
            />
            
            <label style={labelStyle}>Contenido Completo (Cuerpo) *</label>
            <div style={{ background: "white", color: "black", borderRadius: "6px", overflow: "hidden" }}>
              <ReactQuill theme="snow" value={content} onChange={setContent} style={{ height: "350px", marginBottom: "42px" }} />
            </div>
          </div>

          {/* LISTA DE POSTS EXISTENTES */}
          <div style={{ background: "#1e1e1e", padding: "25px", borderRadius: "8px", border: "1px solid #333" }}>
            <h3 style={{ marginTop: 0 }}>Mis Artículos Guardados</h3>
            {loading ? <p>Cargando...</p> : (
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {posts.length === 0 && <p style={{ color: "#888" }}>No hay artículos aún.</p>}
                {posts.map(post => (
                  <div key={post.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "15px", background: editingPostId === post.id ? "#332c10" : "#2a2a2a", borderRadius: "6px", border: editingPostId === post.id ? "1px solid #f59e0b" : "1px solid #444" }}>
                    <div>
                      <div style={{ fontWeight: "bold", fontSize: "16px", marginBottom: "5px", color: editingPostId === post.id ? "#f59e0b" : "white" }}>{post.title}</div>
                      <div style={{ fontSize: "12px", color: post.status === "published" ? "#4ade80" : "#fbbf24" }}>
                        {post.status.toUpperCase()} <span style={{ color: "#888", marginLeft: "10px" }}>/{post.slug}</span>
                      </div>
                    </div>
                    {/* 👇 BOTONES DE ACCIÓN: Editar y Borrar */}
                    <div style={{ display: "flex", gap: "10px" }}>
                      <button type="button" onClick={() => handleEdit(post)} style={{ padding: "8px 12px", background: "#f59e0b", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}>
                        Editar
                      </button>
                      <button type="button" onClick={() => handleDelete(post.id)} style={{ padding: "8px 12px", background: "#ef4444", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}>
                        Borrar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* COLUMNA DERECHA: AJUSTES Y METADATOS */}
        <div style={{ flex: "1", minWidth: "300px", display: "flex", flexDirection: "column", gap: "20px" }}>
          
          <div style={{ background: "#1e1e1e", padding: "25px", borderRadius: "8px", border: "1px solid #333" }}>
            <h3 style={{ marginTop: 0, color: "#3498db" }}>Publicación</h3>


            
          <label style={labelStyle}>Estado</label>
            <select value={status} onChange={(e) => setStatus(e.target.value)} style={{ ...inputStyle, fontWeight: "bold" }}>
              <option value="draft">📁 Borrador (No visible)</option>
              <option value="published">🟢 Publicado (Visible en web)</option>
              <option value="scheduled">⏱️ Programado (Automático)</option> {/* 👈 NUEVA OPCIÓN */}
              <option value="archived">📦 Archivado</option>
            </select>

            {status === "scheduled" && (
              <div style={{ marginTop: "10px", marginBottom: "15px", padding: "15px", background: "#333", borderRadius: "8px", border: "1px solid #f59e0b" }}>
                <label style={{...labelStyle, color: "#f59e0b"}}>¿Cuándo se publicará?</label>
                <input 
                  type="datetime-local" 
                  value={publishedAt}
                  onChange={(e) => setPublishedAt(e.target.value)}
                  style={{...inputStyle, marginBottom: 0}}
                  required={status === "scheduled"}
                />
              </div>
            )}

            {/* 👇 BOTÓN GUARDAR DINÁMICO */}
            <button type="submit" style={{ width: "100%", padding: "15px", background: editingPostId ? "#f59e0b" : "#3498db", color: "white", fontWeight: "bold", border: "none", borderRadius: "6px", cursor: "pointer", fontSize: "16px", marginTop: "10px" }}>
              {editingPostId ? "💾 Actualizar Artículo" : "💾 Guardar Artículo"}
            </button>

            {/* 👇 BOTÓN CANCELAR (Solo aparece si estamos editando) */}
            {editingPostId && (
              <button type="button" onClick={handleCancelEdit} style={{ width: "100%", padding: "12px", background: "#444", color: "white", fontWeight: "bold", border: "none", borderRadius: "6px", cursor: "pointer", fontSize: "14px", marginTop: "10px" }}>
                ❌ Cancelar Edición
              </button>
            )}
          </div>

          <div style={{ background: "#1e1e1e", padding: "25px", borderRadius: "8px", border: "1px solid #333" }}>
            <h3 style={{ marginTop: 0, color: "#e74c3c" }}>Multimedia y Resumen</h3>
            
            <label style={labelStyle}>Imagen Principal (Sube desde tu PC)</label>
            <input 
              type="file" 
              accept="image/*"
              onChange={handleImageUpload}
              disabled={isUploading}
              style={{ ...inputStyle, padding: "8px", background: "#333", cursor: "pointer" }}
            />
            {isUploading && <p style={{ color: "#3498db", fontSize: "14px", marginTop: 0 }}>⏳ Subiendo imagen, por favor espera...</p>}
            
            {featuredImage && !isUploading && (
              <div style={{ position: "relative", marginBottom: "15px" }}>
                <img src={featuredImage} alt="Vista previa" style={{ width: "100%", height: "180px", objectFit: "cover", borderRadius: "6px", border: "2px solid #444" }} />
                <button 
                  type="button" 
                  onClick={() => setFeaturedImage("")} 
                  style={{ position: "absolute", top: "10px", right: "10px", background: "#e74c3c", color: "white", border: "none", borderRadius: "50%", width: "30px", height: "30px", cursor: "pointer", fontWeight: "bold" }}
                >
                  X
                </button>
              </div>
            )}

            <label style={labelStyle}>Resumen Corto (Para la tarjeta)</label>
            <textarea 
              placeholder="Escribe una breve descripción para la vista previa..." 
              value={excerpt} 
              onChange={(e) => setExcerpt(e.target.value)}
              rows={4}
              style={{ ...inputStyle, resize: "vertical" }}
            />
          </div>

          <div style={{ background: "#1e1e1e", padding: "25px", borderRadius: "8px", border: "1px solid #333" }}>
            <h3 style={{ marginTop: 0, color: "#2ecc71" }}>SEO (Opcional)</h3>
            <label style={labelStyle}>Meta Título</label>
            <input 
              type="text" 
              placeholder="Título para Google..." 
              value={metaTitle} 
              onChange={(e) => setMetaTitle(e.target.value)}
              style={inputStyle}
            />

            <label style={labelStyle}>Meta Descripción</label>
            <textarea 
              placeholder="Descripción para resultados de búsqueda..." 
              value={metaDescription} 
              onChange={(e) => setMetaDescription(e.target.value)}
              rows={3}
              style={{ ...inputStyle, resize: "vertical" }}
            />
          </div>

        </div>
      </form>
    </div>
  );
}