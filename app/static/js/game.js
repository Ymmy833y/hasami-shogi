const takeAction = async (player) => {
    const body = document.createElement('div');
    body.classList.add('text-center', 'text-xl');
    body.innerHTML = `${player === 1 ? '先手（歩）' : '後手（と）'}の番`; 
    showModal('', body);

    let selectFromKey = null;
    const possibleMap = await fetchPossibleMoves();    
    if (!possibleMap) return;

    const handleClickWithCell = (toKey) => function() {
        if (selectFromKey) {                        
            sendAction(selectFromKey, toKey);
            selectFromKey = null;
        }
    };

    possibleMap.forEach((toPositions, fromKey) => {
        const fromCell = document.getElementById(fromKey);
        fromCell.addEventListener('click', () => {            
            selectFromKey = fromKey;
            
            resetBoardColors();
            fromCell.style.backgroundColor = 'gold';
            toPositions.forEach(toKey => {
                const toCell = document.getElementById(toKey);
                toCell.style.backgroundColor = 'yellow';

                const handler = handleClickWithCell(toKey);
                toCell.addEventListener('click', handler);
                toCell.handler = handler;
            });
        });
    });
};

const resetBoardColors = () => {        
    const cells = document.querySelectorAll('td');
    cells.forEach(cell => {
        cell.style.backgroundColor = '';
        if (cell.handler) {
            cell.removeEventListener('click', cell.handler);
            delete cell.handler;
        }
    });
};

const updateBoard = (board) => {
    if (!board) throw new Error('');

    const tbodyElem = document.createElement('tbody');
    tbodyElem.innerHTML = `
        ${board.map((row, y) => `
            <tr>${row.map((cell, x) => `
                <td class="border border-gray-400 w-16 h-16 text-center text-lg font-bold bg-yellow-100 hover:bg-yellow-300 cursor-pointer" id="${y+'-'+x}">
                    ${cell === 1 ? '歩' : cell === -1 ? 'と' : ''}
                </td>`).join('')}
            </tr>
        `).join('')}
    `;

    document.querySelector('#board').innerHTML = '';
    document.querySelector('#board').appendChild(tbodyElem);
}

const fetchPossibleMoves = async () => {
    try {
        const res = await fetch('/get_possible_moves');
        if (!res.ok) throw new Error('Network response was not ok');
        const possibleArray = await res.json();
        const possibleMap = new Map();
        possibleArray.forEach(([from, to]) => {
            const fromKey = `${from[0]}-${from[1]}`;
            const toKey = `${to[0]}-${to[1]}`;
            if (!possibleMap.has(fromKey)) {
                possibleMap.set(fromKey, []);
            }
            possibleMap.get(fromKey).push(toKey);
        });
        return possibleMap;
    } catch (error) {
        console.error('Error fetching valid moves:', error);
    }
}

const sendAction = async (fromKey, toKey) => {
    try {
        const response = await fetch('/take_action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                from: fromKey.split('-'),
                to: toKey.split('-')
            }),
        });

        if (response.ok) {
            const result = await response.json();
            updateBoard(result.board);

            if (result.is_valid) {
                if (result.is_finished) {
                    gameSet(result.winner);
                    return;
                }
            } else {
                showModal('エラー', '指定した駒または移動先が不正です');
            }
            takeAction(result.player);
        } else {
            console.error('Failed to move piece:', response.status);
        }
    } catch (error) {
        console.error('Error during move:', error);
    }
}

const gameSet = (winner) => {
    const bodyElem = document.createElement('div');
    bodyElem.classList.add('text-center');
    bodyElem.innerHTML = `
        <p class="mb-4">${winner === 1 ? '先手' : '後手'}の勝ちです</p>
        <a href="#" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-700 focus:outline-none"
            onclick="window.location.reload(); return false;">再ゲーム
        </a>`;
    showModal('ゲーム終了', bodyElem);
}

const showModal = (title, body) => {
    document.querySelector('#modal-title').innerText = title;
    if (body instanceof Element) {
        document.querySelector('#modal-body').innerHTML = '';
        document.querySelector('#modal-body').appendChild(body);
    } else {
        document.querySelector('#modal-body').innerText = body;
    }
    document.querySelector('#modal').classList.remove('hidden');
}
