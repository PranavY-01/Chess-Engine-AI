/**
 * ChessBoard component — renders the 8x8 board with pieces, highlights, and coordinates.
 */
import React from 'react';
import Square from './Square';
import Piece from './Piece';
import type { Board, LegalMove } from '../types/chessTypes';
import './ChessBoard.css';

interface ChessBoardProps {
    board: Board;
    selectedSquare: string | null;
    legalMoves: LegalMove[];
    lastMove: { from: string; to: string } | null;
    isCheck: boolean;
    kingSquare: string | null;
    turn: string;
    readOnly?: boolean;
    branchMode?: boolean;
    hintMove?: { from: string; to: string } | null;
    onSquareClick: (row: number, col: number) => void;
}

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
const RANKS = ['8', '7', '6', '5', '4', '3', '2', '1'];

function squareFromCoords(row: number, col: number): string {
    return FILES[col] + RANKS[row];
}

const ChessBoard: React.FC<ChessBoardProps> = ({
    board,
    selectedSquare,
    legalMoves,
    lastMove,
    isCheck,
    kingSquare,
    turn,
    readOnly = false,
    branchMode = false,
    hintMove = null,
    onSquareClick,
}) => {
    const legalMoveSquares = new Set(legalMoves.map((m) => m.to));

    return (
        <div className="chessboard-wrapper">
            {/* Rank labels (left side) */}
            <div className="rank-labels">
                {RANKS.map((rank) => (
                    <div key={rank} className="rank-label">{rank}</div>
                ))}
            </div>

            <div className={`chessboard ${branchMode ? 'branch-board' : ''}`}>
                {board.map((row, r) =>
                    row.map((piece, c) => {
                        const sq = squareFromCoords(r, c);
                        const isLight = (r + c) % 2 === 0;
                        const isSelected = selectedSquare === sq;
                        const isLegalMove = legalMoveSquares.has(sq);
                        const isLastMoveSquare =
                            lastMove !== null && (lastMove.from === sq || lastMove.to === sq);
                        const isCheckSquare = isCheck && kingSquare === sq;
                        const hasCapture = isLegalMove && piece !== null;

                        return (
                            <Square
                                key={sq}
                                row={r}
                                col={c}
                                isLight={isLight}
                                isSelected={isSelected}
                                isLegalMove={isLegalMove}
                                isLastMove={isLastMoveSquare}
                                isCheck={isCheckSquare}
                                hasCapture={hasCapture}
                                isHintFrom={hintMove?.from === sq}
                                isHintTo={hintMove?.to === sq}
                                disabled={readOnly}
                                onClick={() => onSquareClick(r, c)}
                            >
                                {piece && <Piece code={piece} />}
                            </Square>
                        );
                    })
                )}
            </div>

            {/* File labels (bottom) */}
            <div className="file-labels">
                <div className="file-label-spacer" />
                {FILES.map((file) => (
                    <div key={file} className="file-label">{file}</div>
                ))}
            </div>

            {/* Turn indicator */}
            <div className="turn-indicator">
                <div className={`turn-dot ${turn === 'w' ? 'turn-white' : 'turn-black'}`} />
                <span>{turn === 'w' ? 'White' : 'Black'} to move</span>
            </div>
        </div>
    );
};

export default ChessBoard;
