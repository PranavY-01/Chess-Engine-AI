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
    isHintFrom?: boolean;
    isHintTo?: boolean;
    disabled?: boolean;
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
    isHintFrom = false,
    isHintTo = false,
    disabled = false,
    onClick,
    children,
}) => {
    const classes = [
        'square',
        isLight ? 'square-light' : 'square-dark',
        isSelected ? 'square-selected' : '',
        isLastMove ? 'square-last-move' : '',
        isCheck ? 'square-check' : '',
        isHintFrom ? 'square-hint-from' : '',
        isHintTo ? 'square-hint-to' : '',
        disabled ? 'square-disabled' : '',
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <div className={classes} onClick={disabled ? undefined : onClick} data-square={`${row}-${col}`}>
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
