<script>
    let board = Array(3).fill(" ").map(() => Array(3).fill(" "));
    let buttonsRefs = Array(3).fill(null).map(() => Array(3).fill(null));
    let isPlayerX = true;

    async function handleClick(row, col, buttonElement) {
        if (board[row][col] !== ' ' || !isPlayerX) {
            return;
        }
        buttonElement.disabled = true;
        buttonElement.textContent = 'X';
        isPlayerX = !isPlayerX;
        // const response = await fetch('http://127.0.0.1:3000/tic-tac-toe', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify({ row, col }),
        // });
        //
        // if (!response.ok) {
        //     console.error('HTTP error', response.status);
        //     return;
        // }
        //
        // const updatedBoard = await response.json();
        // board = updatedBoard;
    }
</script>

<style>
    .game {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 90vh;
    }

    .board {
        display: grid;
        grid-template-columns: repeat(3, 0fr);
        gap: 10px;
    }

    h1 {
        font-size: 2.5rem;
        color: #000000;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        font-family: 'Roboto', sans-serif;
    }

    button {
        height: 150px;
        width: 150px;
        font-size: 2rem;
        background: linear-gradient(to right, #b11aff, #db8cff);
        border: none;
        color: white;
        border-radius: 50px;
        box-shadow: 0px 10px 10px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        outline: none;
    }

    button:hover {
        box-shadow: 0px 15px 15px rgba(0, 0, 0, 0.2);
        transform: translateY(-3px);
    }

    button:active {
        transform: translateY(0);
        box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
    }

    button:disabled {
        background: #f1f1f1;
        color: #000000;
        cursor: not-allowed;
    }

    @media (max-height: 600px) {
        button {
            height: 100px;
            width: 100px;
        }
    }

    @media (max-width: 530px) {
        button {
            height: 100px;
            width: 100px;
        }
    }
</style>

<div class="game">
    <div>
        <h1>Tic Tac Toe</h1>
    </div>
    <div class="board">
        {#each board as row, i}
            {#each row as cell, j}
                <button
                    bind:this={buttonsRefs[i][j]}
                    on:click={() => handleClick(i, j, buttonsRefs[i][j])}
                    disabled={cell !== ' '}
                >
                    {cell}
                </button>
            {/each}
        {/each}
    </div>
</div>
