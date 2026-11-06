import type { Character } from '../types/character'

interface CharacterCardProps {
  character: Character
  playerName: string
  editionName: string
  speciesName: string
  backgroundName: string
  onDelete: (id: number) => void
}

export default function CharacterCard({
  character,
  playerName,
  editionName,
  speciesName,
  backgroundName,
  onDelete,
}: CharacterCardProps) {
  return (
    <article className="character-card">
      <div className="character-card-top">
        <div className="character-avatar" aria-hidden="true">
          ♙
        </div>

        <div className="character-card-heading">
          <h3>{character.name}</h3>
          <span>{editionName}</span>
        </div>

        <div className="character-level">
          <span>LEVEL</span>
          <strong>{character.level}</strong>
        </div>
      </div>

      <div className="character-card-details">
        <div>
          <span>SPECIES</span>
          <strong>{speciesName}</strong>
        </div>
        <div>
          <span>BACKGROUND</span>
          <strong>{backgroundName}</strong>
        </div>
        <div>
          <span>PLAYER</span>
          <strong>{playerName}</strong>
        </div>
      </div>

      <div className="character-card-footer">
        <span>
          {character.hit_point_maximum !== null
            ? `${character.hit_point_maximum} HP`
            : 'HP not set'}
        </span>

        <button
          className="text-button danger-text"
          onClick={() => onDelete(character.id)}
          type="button"
        >
          Delete
        </button>
      </div>
    </article>
  )
}
