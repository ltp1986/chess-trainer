/**
 * 前端表单验证工具
 */

const Validator = {
    validatePGN: function(pgn) {
        const errors = [];
        
        if (!pgn || pgn.trim() === '') {
            errors.push('PGN内容不能为空');
            return { valid: false, errors };
        }
        
        const pgnTrimmed = pgn.trim();
        
        if (!pgnTrimmed.startsWith('[')) {
            errors.push('PGN格式不正确，应以[开头');
        }
        
        if (!pgnTrimmed.includes('1.')) {
            errors.push('PGN格式不正确，缺少走法记录');
        }
        
        if (!pgnTrimmed.includes(']')) {
            errors.push('PGN格式不正确，缺少]结束符');
        }
        
        const bracketCount = (pgnTrimmed.match(/\[/g) || []).length;
        const closeBracketCount = (pgnTrimmed.match(/\]/g) || []).length;
        if (bracketCount !== closeBracketCount) {
            errors.push('PGN格式不正确，方括号不匹配');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    },
    
    validatePlayerName: function(name) {
        const errors = [];
        
        if (!name || name.trim() === '') {
            errors.push('姓名不能为空');
        } else if (name.length < 2) {
            errors.push('姓名至少需要2个字符');
        } else if (name.length > 50) {
            errors.push('姓名不能超过50个字符');
        } else if (!/^[\u4e00-\u9fa5a-zA-Z0-9_-]+$/.test(name)) {
            errors.push('姓名只能包含中文、英文、数字、下划线和连字符');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    },
    
    validateEmail: function(email) {
        if (!email || email.trim() === '') {
            return { valid: true, errors: [] };
        }
        
        const errors = [];
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailRegex.test(email)) {
            errors.push('邮箱格式不正确');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    },
    
    validateRating: function(rating) {
        if (!rating) {
            return { valid: true, errors: [] };
        }
        
        const errors = [];
        const numRating = parseInt(rating);
        
        if (isNaN(numRating)) {
            errors.push('评级必须是数字');
        } else if (numRating < 0 || numRating > 3000) {
            errors.push('评级范围应在0-3000之间');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    },
    
    validateLevel: function(level) {
        const validLevels = ['L1', 'L2', 'L3', 'L4'];
        
        if (!level) {
            return { valid: true, errors: [] };
        }
        
        if (!validLevels.includes(level)) {
            return {
                valid: false,
                errors: [`等级必须是 ${validLevels.join('、')} 之一`]
            };
        }
        
        return { valid: true, errors: [] };
    },
    
    validateForm: function(formData) {
        const errors = {};
        
        if (formData.name) {
            const nameResult = this.validatePlayerName(formData.name);
            if (!nameResult.valid) {
                errors.name = nameResult.errors;
            }
        }
        
        if (formData.email) {
            const emailResult = this.validateEmail(formData.email);
            if (!emailResult.valid) {
                errors.email = emailResult.errors;
            }
        }
        
        if (formData.rating) {
            const ratingResult = this.validateRating(formData.rating);
            if (!ratingResult.valid) {
                errors.rating = ratingResult.errors;
            }
        }
        
        if (formData.level) {
            const levelResult = this.validateLevel(formData.level);
            if (!levelResult.valid) {
                errors.level = levelResult.errors;
            }
        }
        
        if (formData.pgn) {
            const pgnResult = this.validatePGN(formData.pgn);
            if (!pgnResult.valid) {
                errors.pgn = pgnResult.errors;
            }
        }
        
        return {
            valid: Object.keys(errors).length === 0,
            errors
        };
    },
    
    showValidationErrors: function(errors, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        for (const [field, fieldErrors] of Object.entries(errors)) {
            fieldErrors.forEach(error => {
                const errorEl = document.createElement('div');
                errorEl.className = 'validation-error';
                errorEl.textContent = `${this.getFieldLabel(field)}: ${error}`;
                container.appendChild(errorEl);
            });
        }
    },
    
    getFieldLabel: function(field) {
        const labels = {
            name: '姓名',
            email: '邮箱',
            rating: '评级',
            level: '等级',
            pgn: 'PGN内容'
        };
        return labels[field] || field;
    },
    
    validateMove: function(move, validMoves) {
        return validMoves.includes(move);
    },
    
    validateFEN: function(fen) {
        if (!fen || fen.trim() === '') {
            return { valid: false, errors: ['FEN不能为空'] };
        }
        
        const parts = fen.trim().split(' ');
        if (parts.length < 6) {
            return { valid: false, errors: ['FEN格式不正确'] };
        }
        
        const boardPart = parts[0];
        const rows = boardPart.split('/');
        if (rows.length !== 8) {
            return { valid: false, errors: ['棋盘行数不正确'] };
        }
        
        for (const row of rows) {
            let count = 0;
            for (const char of row) {
                if (/\d/.test(char)) {
                    count += parseInt(char);
                } else if (/[PNBRQKpnbrqk]/.test(char)) {
                    count++;
                } else {
                    return { valid: false, errors: ['FEN包含无效字符'] };
                }
            }
            if (count !== 8) {
                return { valid: false, errors: ['每行必须有8个格子'] };
            }
        }
        
        if (!/^[wb]$/.test(parts[1])) {
            return { valid: false, errors: ['回合标识不正确'] };
        }
        
        return { valid: true, errors: [] };
    }
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = Validator;
}