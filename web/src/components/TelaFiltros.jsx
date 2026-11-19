import { useEffect, useState } from "react";
import "./TelaFiltros.css";

/** Valores controlados pelo componente pai; nenhum acesso à API é necessário. */
export const FILTROS_PADRAO = {
  criterio: "menor_custo",
  modais: [],
  precoMaximo: null,
  acomodacao: null,
};

const CRITERIOS = [
  { id: "menor_custo", rotulo: "Menor custo" },
  { id: "menor_tempo", rotulo: "Menor tempo" },
  { id: "mais_confiavel", rotulo: "Mais confiável" },
];

const GRUPOS = [
  {
    categoria: "fluvial",
    titulo: "Fluvial",
    modais: ["Balsa pequena", "Balsa grande", "Barco regional", "Voadeira"],
  },
  {
    categoria: "rodoviario",
    titulo: "Rodoviário",
    modais: ["Carro", "Ônibus", "Moto-táxi"],
  },
  {
    categoria: "aereo",
    titulo: "Aéreo",
    modais: ["Táxi aéreo", "Avião regional", "Helicóptero"],
  },
];

export function converterPreco(texto) {
  if (!texto || !String(texto).trim()) return null;
  const valor = String(texto).trim().replace(/\s|R\$/g, "");
  // Aceita 350,50; 1.250,00; 350.50; 350 e 1250.
  const normalizado = valor.includes(",")
    ? valor.replace(/\./g, "").replace(",", ".")
    : /^\d+\.\d{3}(?:\.\d{3})*$/.test(valor)
      ? valor.replace(/\./g, "")
      : valor;
  const numero = Number(normalizado);
  return Number.isFinite(numero) && numero >= 0 ? numero : NaN;
}

function prepararFiltros(filtros = {}) {
  return {
    criterio: filtros.criterio ?? FILTROS_PADRAO.criterio,
    modais: Array.isArray(filtros.modais) ? [...filtros.modais] : [],
    precoMaximo: filtros.precoMaximo == null ? "" : String(filtros.precoMaximo),
    acomodacao: filtros.acomodacao ?? null,
  };
}

/**
 * @param {Object} props
 * @param {Object} [props.filtrosIniciais] Filtros já aplicados no app
 * @param {(filtros: Object) => void} props.onAplicar Volta à busca com os filtros escolhidos
 * @param {() => void} [props.onVoltar] Volta sem aplicar alterações
 */
export default function TelaFiltros({ filtrosIniciais = FILTROS_PADRAO, onAplicar, onVoltar }) {
  const [filtros, setFiltros] = useState(() => prepararFiltros(filtrosIniciais));
  const [erroPreco, setErroPreco] = useState("");

  useEffect(() => {
    setFiltros(prepararFiltros(filtrosIniciais));
    setErroPreco("");
  }, [filtrosIniciais]);

  function alternarModal(modal) {
    setFiltros((anterior) => {
      const selecionado = anterior.modais.includes(modal);
      const modais = selecionado
        ? anterior.modais.filter((item) => item !== modal)
        : [...anterior.modais, modal];
      return {
        ...anterior,
        modais,
        acomodacao: modais.includes("Barco regional") ? anterior.acomodacao : null,
      };
    });
  }

  function limpar() {
    setFiltros(prepararFiltros(FILTROS_PADRAO));
    setErroPreco("");
  }

  function aplicar(evento) {
    evento.preventDefault();
    const precoMaximo = converterPreco(filtros.precoMaximo);
    if (Number.isNaN(precoMaximo)) {
      setErroPreco("Informe um preço válido, como 350 ou 1.250,00.");
      return;
    }
    setErroPreco("");
    onAplicar?.({
      criterio: filtros.criterio,
      modais: [...filtros.modais],
      precoMaximo,
      acomodacao: filtros.modais.includes("Barco regional") ? filtros.acomodacao : null,
    });
  }

  const mostraAcomodacao = filtros.modais.includes("Barco regional");

  return (
    <main className="tela-filtros">
      <header className="tela-filtros__cabecalho">
        <div className="tela-filtros__cabecalho-interno">
          {onVoltar && (
            <button type="button" className="tela-filtros__voltar" onClick={onVoltar} aria-label="Voltar à busca">‹</button>
          )}
          <div>
            <p className="tela-filtros__marca">EMBARQUE AMAZÔNIA</p>
            <h1>Critérios e filtros</h1>
            <p>Personalize as opções de rota.</p>
          </div>
        </div>
      </header>

      <form onSubmit={aplicar}>
        <div className="tela-filtros__conteudo">
          <fieldset className="tela-filtros__grupo">
            <legend>Ordenar por</legend>
            <div className="tela-filtros__criterios">
              {CRITERIOS.map(({ id, rotulo }) => (
                <label key={id} className={`tela-filtros__criterio ${filtros.criterio === id ? "is-active" : ""}`}>
                  <input
                    type="radio"
                    name="criterio"
                    value={id}
                    checked={filtros.criterio === id}
                    onChange={() => setFiltros((prev) => ({ ...prev, criterio: id }))}
                  />
                  <span>{rotulo}</span>
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset className="tela-filtros__grupo">
            <legend>Modais de transporte</legend>
            <p className="tela-filtros__auxiliar">Sem seleção: considere todos os modais.</p>
            {GRUPOS.map(({ categoria, titulo, modais }) => (
              <div key={categoria} className={`tela-filtros__categoria tela-filtros__categoria--${categoria}`}>
                <h2>{titulo}</h2>
                <div className="tela-filtros__chips">
                  {modais.map((modal) => (
                    <button
                      type="button"
                      key={modal}
                      className={`tela-filtros__chip ${filtros.modais.includes(modal) ? "is-active" : ""}`}
                      aria-pressed={filtros.modais.includes(modal)}
                      onClick={() => alternarModal(modal)}
                    >
                      {filtros.modais.includes(modal) ? "✓ " : "+ "}{modal}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </fieldset>

          <div className="tela-filtros__grupo">
            <label className="tela-filtros__titulo-campo" htmlFor="preco-maximo">Preço máximo (opcional)</label>
            <div className="tela-filtros__preco">
              <span>R$</span>
              <input
                id="preco-maximo"
                type="text"
                inputMode="decimal"
                placeholder="Ex.: 350,00"
                value={filtros.precoMaximo}
                aria-invalid={Boolean(erroPreco)}
                aria-describedby={erroPreco ? "erro-preco" : undefined}
                onChange={(e) => {
                  setFiltros((prev) => ({ ...prev, precoMaximo: e.target.value }));
                  setErroPreco("");
                }}
              />
            </div>
            {erroPreco && <p role="alert" id="erro-preco" className="tela-filtros__erro">{erroPreco}</p>}
          </div>

          {mostraAcomodacao && (
            <fieldset className="tela-filtros__grupo">
              <legend>Acomodação — Barco regional</legend>
              <div className="tela-filtros__acomodacoes">
                {['Rede', 'Camarote'].map((opcao) => (
                  <button
                    key={opcao}
                    type="button"
                    className={`tela-filtros__acomodacao ${filtros.acomodacao === opcao ? "is-active" : ""}`}
                    aria-pressed={filtros.acomodacao === opcao}
                    onClick={() => setFiltros((prev) => ({ ...prev, acomodacao: prev.acomodacao === opcao ? null : opcao }))}
                  >
                    {opcao}
                  </button>
                ))}
              </div>
            </fieldset>
          )}
        </div>
        <footer className="tela-filtros__rodape">
          <button className="tela-filtros__botao tela-filtros__botao--limpar" type="button" onClick={limpar}>Limpar</button>
          <button className="tela-filtros__botao tela-filtros__botao--aplicar" type="submit">Aplicar</button>
        </footer>
      </form>
    </main>
  );
}
