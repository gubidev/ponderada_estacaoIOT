document.addEventListener('DOMContentLoaded', function() {
    // Se existir um canvas na tela, carrega o gráfico
    if (document.getElementById('graficoSensores')) {
        carregarGrafico();
    }
});

// Busca os dados da API e monta o gráfico
async function carregarGrafico() {
    try {
        const response = await fetch('/api/leituras/recentes');
        const dados = await response.json();

        // Invertendo os dados para o gráfico ir do mais antigo para o mais novo
        dados.reverse();

        const labels = dados.map(d => d.timestamp.split(' ')[1]); // Pega só a hora
        const temperaturas = dados.map(d => d.temperatura);
        const umidades = dados.map(d => d.umidade);

        const ctx = document.getElementById('graficoSensores').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Temperatura (°C)',
                        data: temperaturas,
                        borderColor: '#e74c3c',
                        tension: 0.4
                    },
                    {
                        label: 'Umidade (%)',
                        data: umidades,
                        borderColor: '#3498db',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } catch (error) {
        console.error('Erro ao carregar o gráfico:', error);
    }
}

// Envia uma requisição DELETE para a API
async function deletarLeitura(id) {
    if (confirm('Tem certeza que deseja excluir esta leitura?')) {
        const response = await fetch(`/leituras/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            window.location.reload(); // Recarrega a página para atualizar a tabela
        } else {
            alert('Erro ao excluir a leitura.');
        }
    }
}

// Captura os dados do formulário e envia via PUT
async function atualizarLeitura(event, id) {
    event.preventDefault(); // Impede o envio padrão do formulário

    const payload = {
        temperatura: document.getElementById('temp').value,
        umidade: document.getElementById('umid').value,
        pressao: document.getElementById('pressao').value || null
    };

    const response = await fetch(`/leituras/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (response.ok) {
        alert('Leitura atualizada com sucesso!');
        window.location.href = '/historico'; // Redireciona de volta para o histórico
    } else {
        alert('Erro ao atualizar a leitura.');
    }
}
