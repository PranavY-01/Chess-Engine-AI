/**
 * Square component — renders a single chess board square with visual states.
 */
import React from 'react';
import './Square.css';

interface SquareProps {
    row: number;
    col: number;
    isLight: boolean;
    isSelected: boolean;
    isLegalMove: boolean;
    isLastMove: boolean;
    isCheck: boolean;
    hasCapture: boolean;
    onClick: () => void;
    children?: React.ReactNode;
}

const Square: React.FC<SquareProps> = ({
    row,
    col,
    isLight,
    isSelected,
    isLegalMove,
    isLastMove,
    isCheck,
    hasCapture,
    onClick,
    children,
}) => {
    const classes = [
        'square',
        isLight ? 'square-light' : 'square-dark',
        isSelected ? 'square-selected' : '',
        isLastMove ? 'square-last-move' : '',
        isCheck ? 'square-check' : '',
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={classes} onClick={onClick} data-square={`${row}-${col}`}>
            {children}
            {isLegalMove && !hasCapture && (
                <div className="legal-move-dot" />
            )}
            {isLegalMove && hasCapture && (
                <div className="legal-move-capture" />
            )}
        </div>
    );
};

export default Square;
