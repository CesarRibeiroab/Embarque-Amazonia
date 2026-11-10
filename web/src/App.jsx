import React, { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export default function App() {
  const [origem, setOrigem] = useState('Belém');
  const [destino, setDestino] = useState('Manaus');
  const [dataViagem, setDataViagem] = useState('2026-11-20');
  const [criterio, setCriterio] = useState('menor_tempo');
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);
  const [resultado, setResultado] = useState(null);

  const buscarRotas = async (e) => {
    e.preventDefault();
    setCarregando(true);
    setErro(null);
    try {
      const params = new URLSearchParams({
        origem,
        destino,
        criterio,
      });
      if (dataViagem) {
        params.append('data', dataViagem);
      }

      const res = await fetch(`${API_BASE}/rotas?${params.toString()}`);
      const data = await res.json();

      if (!res.ok) {
        setErro(data.mensagem || 'Erro ao consultar rotas.');
        setResultado(null);
      } else {
        setResultado(data);
      }
    } catch (err) {
      setErro('Não foi possível conectar à API. Verifique se o servidor FastAPI está ativo em localhost:8000.');
      setResultado(null);
    } finally {
      setCarregando(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <header style={{ marginBottom: '20px', borderBottom: '2px solid #319795', paddingBottom: '10px' }}>
        <h1 style={{ margin: 0, fontSize: '1.4rem', color: '#234e52' }}>Embarque Amazônia</h1>
        <p style={{ margin: '5px 0 0 0', fontSize: '0.85rem', color: '#718096' }}>
          Hub Multimodal de Passageiros para a Amazônia Legal
        </p>
      </header>

      <form onSubmit={buscarRotas} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '4px' }}>
            Origem
          </label>
          <input
            type="text"
            value={origem}
            onChange={(e) => setOrigem(e.target.value)}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #cbd5e0' }}
            required
          />
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '4px' }}>
            Destino
          </label>
          <input
            type="text"
            value={destino}
            onChange={(e) => setDestino(e.target.value)}
            style={{ width: '100%', padding: '8px', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #cbd5e0' }}
            required
          />
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '4px' }}>
              Data da Viagem
            </label>
            <input
              type="date"
              value={dataViagem}
              onChange={(e) => setDataViagem(e.target.value)}
              style={{ width: '100%', padding: '8px', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #cbd5e0' }}
            />
          </div>

          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '4px' }}>
              Critério
            </label>
            <select
              value={criterio}
              onChange={(e) => setCriterio(e.target.value)}
              style={{ width: '100%', padding: '8px', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #cbd5e0' }}
            >
              <option value="menor_tempo">Menor tempo</option>
              <option value="menor_custo">Menor custo</option>
              <option value="mais_confiavel">Mais confiável</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={carregando}
          style={{
            backgroundColor: '#319795',
            color: 'white',
            border: 'none',
            padding: '12px',
            borderRadius: '6px',
            fontWeight: 'bold',
            cursor: 'pointer',
            marginTop: '8px'
          }}
        >
          {carregando ? 'Buscando opções...' : 'Buscar Rotas'}
        </button>
      </form>

      {erro && (
        <div style={{ marginTop: '20px', padding: '12px', background: '#fed7d7', color: '#9b2c2c', borderRadius: '6px', fontSize: '0.9rem' }}>
          {erro}
        </div>
      )}

      {resultado && (
        <div style={{ marginTop: '24px' }}>
          <h2 style={{ fontSize: '1.1rem', color: '#2d3748', marginBottom: '12px' }}>
            Opções encontradas ({resultado.total_opcoes})
          </h2>

          {resultado.rotas.length === 0 ? (
            <p style={{ color: '#718096', fontSize: '0.9rem' }}>
              Nenhuma rota encontrada para este itinerário na data selecionada.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {resultado.rotas.map((rota) => (
                <div
                  key={rota.id}
                  style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    padding: '14px',
                    background: '#ffffff',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.06)'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 'bold', color: '#2b6cb0' }}>
                      {rota.modais.join(' + ')}
                    </span>
                    <span style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#276749' }}>
                      R$ {rota.preco_total.toFixed(2)}
                    </span>
                  </div>

                  <div style={{ marginTop: '6px', fontSize: '0.85rem', color: '#4a5568' }}>
                    <strong>Duração:</strong> {rota.duracao_total_formatada} • {rota.numero_trechos} trecho(s)
                    {rota.numero_conexoes > 0 && ` (${rota.numero_conexoes} conexão)`}
                  </div>

                  <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {rota.selo.map((s, idx) => (
                      <span
                        key={idx}
                        style={{
                          fontSize: '0.75rem',
                          padding: '2px 8px',
                          borderRadius: '12px',
                          background: s === 'Menor tempo' ? '#e2e8f0' : s === 'Menor custo' ? '#c6f6d5' : '#bee3f8',
                          color: '#2d3748',
                          fontWeight: 'bold'
                        }}
                      >
                        {s}
                      </span>
                    ))}
                  </div>

                  <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#a0aec0' }}>
                    {rota.atualizado_em}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
