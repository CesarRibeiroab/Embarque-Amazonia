/** Componente pequeno para INSERIR na lista do autocomplete existente (P02). */
const TIPOS_CANONICOS = {
  "Belém": "Cidade",
  "Santarém": "Cidade",
  "Manaus": "Cidade",
  "Tefé": "Cidade",
  "Parintins": "Cidade",
  "Cametá": "Cidade",
  "Alenquer": "Cidade",
  "Porto da Manaus Moderna": "Porto",
  "Aeroporto Eduardo Gomes": "Aeroporto",
};
const ICONE = { Cidade: "🏙", Porto: "⚓", Aeroporto: "✈" };

export function tipoDaLocalidade(localidade) {
  const nome = typeof localidade === "string" ? localidade : localidade?.nome;
  return (typeof localidade === "object" && localidade?.tipo) || TIPOS_CANONICOS[nome] || "Localidade";
}

export default function SugestoesLocalidades({ sugestoes = [], onSelecionar }) {
  if (!sugestoes.length) return <p role="status">Localidade não encontrada</p>;

  return (
    <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {sugestoes.map((localidade) => {
        const nome = typeof localidade === "string" ? localidade : localidade.nome;
        const tipo = tipoDaLocalidade(localidade);
        return (
          <li key={typeof localidade === "object" ? (localidade.id ?? nome) : nome}>
            <button
              type="button"
              onClick={() => onSelecionar?.(localidade)}
              style={{ width: "100%", display: "flex", alignItems: "center", gap: 12, textAlign: "left", padding: 12, border: "0", borderBottom: "1px solid #D1D5DB", background: "#fff", color: "#1A1A1A", cursor: "pointer", font: "inherit" }}
            >
              <span aria-hidden="true" style={{ fontSize: 20 }}>{ICONE[tipo] ?? "📍"}</span>
              <span style={{ display: "grid", gap: 2 }}>
                <strong style={{ fontSize: 14 }}>{nome}</strong>
                <small style={{ color: "#6B7280", fontSize: 12 }}>{tipo}</small>
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
