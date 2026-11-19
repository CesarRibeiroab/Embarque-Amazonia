/** Use somente na P04, junto do hook useComparacao. */
export default function BarraComparacao({ selecionadas = [], onComparar, deslocamentoInferior = 0 }) {
  const habilitado = selecionadas.length >= 2 && selecionadas.length <= 3;
  return (
    <aside
      aria-label="Comparação de rotas"
      style={{ position: "fixed", bottom: deslocamentoInferior, left: 0, right: 0, zIndex: 10, padding: "12px 16px", borderTop: "1px solid #D1D5DB", background: "#FFFFFF" }}
    >
      <div style={{ maxWidth: 540, margin: "0 auto" }}>
        <button
          type="button"
          disabled={!habilitado}
          onClick={() => habilitado && onComparar?.(selecionadas)}
          style={{ width: "100%", minHeight: 48, padding: "12px 16px", border: 0, borderRadius: 8, font: "600 14px Inter, Arial, sans-serif", background: habilitado ? "#1B5E3F" : "#D1D5DB", color: habilitado ? "#FFFFFF" : "#6B7280", cursor: habilitado ? "pointer" : "not-allowed" }}
        >
          Comparar ({selecionadas.length})
        </button>
      </div>
    </aside>
  );
}
