import { useState } from "react";

/**
 * Use no componente que renderiza os cards P04.
 * Cada opção PRECISA ter um `id` único. A seleção fica local; não depende da API.
 */
export default function useComparacao() {
  const [selecionadas, setSelecionadas] = useState([]);

  function alternarComparacao(opcao) {
    if (!opcao || opcao.id == null) {
      throw new Error("Cada opção de rota precisa de um id único para comparar.");
    }
    setSelecionadas((anteriores) => {
      if (anteriores.some((item) => item.id === opcao.id)) {
        return anteriores.filter((item) => item.id !== opcao.id);
      }
      if (anteriores.length >= 3) return anteriores;
      return [...anteriores, opcao];
    });
  }

  function estaSelecionada(id) {
    return selecionadas.some((item) => item.id === id);
  }

  return {
    selecionadas,
    alternarComparacao,
    estaSelecionada,
    limparComparacao: () => setSelecionadas([]),
    podeComparar: selecionadas.length >= 2 && selecionadas.length <= 3,
  };
}
