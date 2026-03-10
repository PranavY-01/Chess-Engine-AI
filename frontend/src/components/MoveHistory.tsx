/**
 * MoveHistory component — scrollable move list with navigation.
 */
import React, { useRef, useEffect } from 'react';
import './MoveHistory.css';

interface MoveHistoryProps {
    moves: string[];
    onUndo: () => void;
    onRedo: () => void;
    canUndo: boolean;
    canRedo: boolean;
}

const MoveHistory: React.FC<MoveHistoryProps> = ({
    moves,
    onUndo,
    onRedo,
    canUndo,
    canRedo,
}) => {
    const listRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (listRef.current) {
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [moves]);

    return (
        <div className="move-history-panel">
            <h3 className="panel-title">
                <span className="panel-icon">📜</span>
                Move History
            </h3>

            <div className="move-list" ref={listRef}>
                {moves.length === 0 ? (
                    <div className="no-moves">No moves yet</div>
                ) : (
                    moves.map((move, idx) => (
                        <div key={idx} className="move-entry">
                            {move}
                        </div>
                    ))
                )}
            </div>

            <div className="nav-buttons">
                <button
                    className="nav-btn"
                    onClick={onUndo}
                    disabled={!canUndo}
                    title="Undo"
                >
                    ↶ Undo
                </button>
                <button
                    className="nav-btn"
                    onClick={onRedo}
                    disabled={!canRedo}
                    title="Redo"
                >
                    ↷ Redo
                </button>
            </div>
        </div>
    );
};

export default MoveHistory;
