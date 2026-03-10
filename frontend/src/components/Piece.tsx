/**
 * Piece component — renders a chess piece using Unicode symbols.
 */
import React from 'react';
import { PIECE_SYMBOLS } from '../types/chessTypes';
import './Piece.css';

interface PieceProps {
    code: string;
    isDragging?: boolean;
}

const Piece: React.FC<PieceProps> = ({ code, isDragging }) => {
    const symbol = PIECE_SYMBOLS[code] || '';
    const color = code[0] === 'w' ? 'white' : 'black';

    return (
        <span
            className={`chess-piece piece-${color} ${isDragging ? 'dragging' : ''}`}
            data-piece={code}
        >
            {symbol}
        </span>
    );
};

export default Piece;
