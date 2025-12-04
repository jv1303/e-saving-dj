document.addEventListener('DOMContentLoaded', function() {
    // Máscaras para todos os formulários
    aplicarMascaras();
    
    // Validação em tempo real
    inicializarValidacoes();
});

function aplicarMascaras() {
    // Máscara para telefone
    const telefoneInputs = document.querySelectorAll('input[name="telefone"]');
    telefoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) {
                value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
            } else if (value.length > 6) {
                value = value.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, '($1) $2-$3');
            } else if (value.length > 2) {
                value = value.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
            } else if (value.length > 0) {
                value = value.replace(/^(\d*)/, '($1');
            }
            e.target.value = value;
        });
    });
    
    // Máscara para CEP
    const cepInputs = document.querySelectorAll('input[name="cep"]');
    cepInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 5) {
                value = value.replace(/^(\d{5})(\d{0,3}).*/, '$1-$2');
            }
            e.target.value = value;
        });
    });
    
    // Máscara para CPF/CNPJ
    const cpfCnpjInputs = document.querySelectorAll('input[name="cpf_cnpj"]');
    cpfCnpjInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 11) {
                // CNPJ
                value = value.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2})/, '$1.$2.$3/$4-$5');
            } else {
                // CPF
                value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{0,2})/, '$1.$2.$3-$4');
            }
            e.target.value = value;
        });
    });
}

function inicializarValidacoes() {
    const forms = document.querySelectorAll('form[novalidate]');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validarCampo(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                    const feedback = this.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.remove();
                    }
                }
            });
        });
        
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validarCampo(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Rolar até o primeiro erro
                const primeiroErro = form.querySelector('.is-invalid');
                if (primeiroErro) {
                    primeiroErro.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    });
}

function validarCampo(campo) {
    const valor = campo.value.trim();
    const tipo = campo.type;
    const nome = campo.name;
    
    // Remover mensagens de erro anteriores
    const feedbackExistente = campo.nextElementSibling;
    if (feedbackExistente && feedbackExistente.classList.contains('invalid-feedback')) {
        feedbackExistente.remove();
    }
    
    // Validações específicas
    if (campo.required && valor === '') {
        mostrarErro(campo, 'Este campo é obrigatório.');
        return false;
    }
    
    if (nome === 'email' && valor !== '') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(valor)) {
            mostrarErro(campo, 'Por favor, insira um e-mail válido.');
            return false;
        }
    }
    
    if (nome === 'telefone' && valor !== '') {
        const telefoneLimpo = valor.replace(/\D/g, '');
        if (telefoneLimpo.length !== 11) {
            mostrarErro(campo, 'Telefone deve ter 11 dígitos.');
            return false;
        }
    }
    
    if (nome === 'cep' && valor !== '') {
        const cepLimpo = valor.replace(/\D/g, '');
        if (cepLimpo.length !== 8) {
            mostrarErro(campo, 'CEP deve ter 8 dígitos.');
            return false;
        }
    }
    
    if (nome === 'cpf_cnpj' && valor !== '') {
        const cpfCnpjLimpo = valor.replace(/\D/g, '');
        if (![11, 14].includes(cpfCnpjLimpo.length)) {
            mostrarErro(campo, 'CPF deve ter 11 dígitos ou CNPJ 14 dígitos.');
            return false;
        }
    }
    
    // Se passou em todas as validações
    if (campo.classList.contains('is-invalid')) {
        campo.classList.remove('is-invalid');
    }
    
    return true;
}

function mostrarErro(campo, mensagem) {
    campo.classList.add('is-invalid');
    
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = mensagem;
    
    campo.parentNode.appendChild(feedback);
}