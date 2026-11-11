const brlFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
});

export function formatarMoeda(valor) {
  const num = Number(valor);
  if (!Number.isFinite(num)) {
    return brlFormatter.format(0);
  }
  return brlFormatter.format(num);
}

export function formatarDuracao(minutosTotal) {
  const total = Math.max(0, Math.round(Number(minutosTotal) || 0));
  const dias = Math.floor(total / (24 * 60));
  const horas = Math.floor((total % (24 * 60)) / 60);
  const mins = total % 60;

  const partes = [];
  if (dias > 0) partes.push(`${dias} d`);
  if (horas > 0) partes.push(`${horas} h`);
  if (mins > 0 || partes.length === 0) partes.push(`${mins} min`);
  return partes.join(' ');
}

export function formatarData(isoDate) {
  if (!isoDate || typeof isoDate !== 'string') return '';
  const limpa = isoDate.trim().slice(0, 10);
  const match = limpa.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return isoDate;
  const [, ano, mes, dia] = match;
  return `${dia}/${mes}/${ano}`;
}

export function formatarRecencia(dias) {
  const n = Number(dias);
  if (!Number.isFinite(n) || n <= 0) return 'Atualizado hoje';
  if (n === 1) return 'Atualizado há 1 dia';
  return `Atualizado há ${n} dias`;
}

export function formatarConexoes(numConexoes) {
  const n = Math.max(0, Number(numConexoes) || 0);
  if (n === 0) return 'sem conexões';
  if (n === 1) return '1 conexão';
  return `${n} conexões`;
}

export function corCategoriaModal(nomeModal = '') {
  const norm = nomeModal
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();

  if (norm.includes('aviao') || norm.includes('taxi') || norm.includes('helicoptero')) {
    return '#6A4C93'; // Aéreo
  }
  if (norm.includes('carro') || norm.includes('onibus') || norm.includes('moto')) {
    return '#D9822B'; // Rodoviário
  }
  return '#1F6FB2'; // Fluvial (padrão amazônico)
}

export function estiloSelo(selo) {
  switch (selo) {
    case 'Menor custo':
      return { backgroundColor: '#2E7D32', color: '#FFFFFF' };
    case 'Menor tempo':
      return { backgroundColor: '#1F6FB2', color: '#FFFFFF' };
    case 'Mais confiável':
      return { backgroundColor: '#00796B', color: '#FFFFFF' };
    case 'Desatualizado':
      return { backgroundColor: '#F2A900', color: '#1A1A1A' };
    default:
      return { backgroundColor: '#D1D5DB', color: '#1A1A1A' };
  }
}

