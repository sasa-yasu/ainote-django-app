document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.toggle-collapse-btn');

    // openSectionsInput を取得 or 自動生成
    let openSectionsInput = document.getElementById('openSectionsInput');
    if (!openSectionsInput) {
        openSectionsInput = document.createElement('input');
        openSectionsInput.type = 'hidden';
        openSectionsInput.id = 'openSectionsInput';
        document.body.appendChild(openSectionsInput);
    }

    function updateOpenSections(id) {
        const cleanId = id.replace(/^#/, ''); // #を除去
        const ids = openSectionsInput.value ? openSectionsInput.value.split(',') : [];
        if (!ids.includes(cleanId)) {
            ids.push(cleanId);
        }
        openSectionsInput.value = ids.join(',');
    }

    function removeOpenSection(id) {
        const cleanId = id.replace(/^#/, '');
        const ids = openSectionsInput.value ? openSectionsInput.value.split(',') : [];
        openSectionsInput.value = ids.filter(i => i !== cleanId).join(',');
    }

    function setButtonState(button, isOpen, showText, hideText) {
        button.textContent = isOpen ? hideText : showText;
    
        if (isOpen) {
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-outline-secondary');
        } else {
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-outline-primary');
        }
    }
    
    buttons.forEach(button => {
        const targetSelector = button.getAttribute('data-bs-target');
        if (!targetSelector || !targetSelector.startsWith('#')) return;

        const target = document.querySelector(targetSelector);
        if (!target) return;

        const showText = button.getAttribute('data-text-show') || '表示';
        const hideText = button.getAttribute('data-text-hide') || '非表示';

        // 初期状態に応じたラベル・クラス設定
        setButtonState(button, target.classList.contains('show'), showText, hideText);

        // Bootstrap の collapse イベントを個別に紐付け
        target.addEventListener('show.bs.collapse', function (e) {
            if (e.target === target) {
                setButtonState(button, true, showText, hideText);
                updateOpenSections(targetSelector);
            }
        });

        target.addEventListener('hide.bs.collapse', function (e) {
            if (e.target === target) {
                setButtonState(button, false, showText, hideText);
                removeOpenSection(targetSelector);
            }
        });

    });

    // ページロード時、開いておくセクションを反映
    const raw = openSectionsInput.value || '';
    const toOpen =  raw.replace(/[\[\]'"\s]/g, '').split(',').filter(Boolean);  // safety cleanup
    toOpen.forEach(id => {
        const el = document.querySelector('#' + id);
        if (el && !el.classList.contains('show')) {
            new bootstrap.Collapse(el, { toggle: true });
        }
    });
});