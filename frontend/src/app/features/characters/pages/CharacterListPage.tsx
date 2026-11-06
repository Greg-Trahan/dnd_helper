import { useEffect, useState } from 'react'

import CharacterCard from '../components/characterCard'
import {
  deleteCharacter,
  getCharacters,
} from '../services/characterService'
import {
  getBackgrounds,
  getEditions,
  getPlayers,
  getSpecies,
} from '../services/referenceDataService'

import type { Character } from '../types/character'
import type {
  BackgroundOption,
  EditionOption,
  PlayerOption,
  SpeciesOption,
} from '../types/referenceData'

interface CharacterData {
  characters: Character[]
  players: PlayerOption[]
  editions: EditionOption[]
  species: SpeciesOption[]
  backgrounds: BackgroundOption[]
}

const emptyData: CharacterData = {
  characters: [],
  players: [],
  editions: [],
  species: [],
  backgrounds: [],
}

async function fetchCharacterData(): Promise<CharacterData> {
  const [
    characters,
    players,
    editions,
    species,
    backgrounds,
  ] = await Promise.all([
    getCharacters(),
    getPlayers(),
    getEditions(),
    getSpecies(),
    getBackgrounds(),
  ])

  return {
    characters,
    players,
    editions,
    species,
    backgrounds,
  }
}

export default function CharacterListPage() {
  const [data, setData] = useState<CharacterData>(emptyData)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  useEffect(() => {
    let active = true

    async function loadInitialCharacters() {
      try {
        const result = await fetchCharacterData()

        if (active) {
          setData(result)
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load characters.',
          )
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadInitialCharacters()

    return () => {
      active = false
    }
  }, [])

  async function loadCharacters() {
    setLoading(true)
    setError(null)

    try {
      const result = await fetchCharacterData()
      setData(result)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load characters.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete(id: number) {
    const character = data.characters.find((item) => item.id === id)

    if (!character) return

    const confirmed = window.confirm(
      `Are you sure you want to delete ${character.name}? This cannot be undone.`,
    )

    if (!confirmed) return

    setDeletingId(id)
    setError(null)

    try {
      await deleteCharacter(id)

      setData((current) => ({
        ...current,
        characters: current.characters.filter(
          (item) => item.id !== id,
        ),
      }))
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to delete character.',
      )
    } finally {
      setDeletingId(null)
    }
  }

  const playerNames = new Map(
    data.players.map((item) => [item.id, item.name]),
  )
  const editionNames = new Map(
    data.editions.map((item) => [item.id, item.name]),
  )
  const speciesNames = new Map(
    data.species.map((item) => [item.id, item.name]),
  )
  const backgroundNames = new Map(
    data.backgrounds.map((item) => [item.id, item.name]),
  )

  return (
    <section className="characters-page">
      <div className="characters-page-heading">
        <div>
          <div className="eyebrow">YOUR ADVENTURERS</div>
          <h1>Characters</h1>
          <p>Build heroes, manage their details, and prepare for adventure.</p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={() => setNotice(
            'The character creation form is the next part of the builder.',
          )}
        >
          <span aria-hidden="true">＋</span>
          Create character
        </button>
      </div>

      {notice && (
        <div className="character-notice" role="status">
          {notice}
          <button
            className="text-button"
            type="button"
            onClick={() => setNotice(null)}
            aria-label="Dismiss message"
          >
            Dismiss
          </button>
        </div>
      )}

      {error && (
        <div className="character-error" role="alert">
          <span>{error}</span>
          <button
            className="secondary-button"
            type="button"
            onClick={() => void loadCharacters()}
          >
            Try again
          </button>
        </div>
      )}

      {loading ? (
        <div className="character-state">
          <div className="loading-symbol" aria-hidden="true">✧</div>
          <p>Gathering your adventurers...</p>
        </div>
      ) : data.characters.length === 0 ? (
        <div className="character-empty">
          <div className="placeholder-icon" aria-hidden="true">♙</div>
          <h2>Your story begins with a hero.</h2>
          <p>
            You haven't created any characters yet. Your next great
            adventure is waiting.
          </p>
          <button
            className="primary-button"
            type="button"
            onClick={() => setNotice(
              'The character creation form is the next part of the builder.',
            )}
          >
            Create your first character
          </button>
        </div>
      ) : (
        <>
          <div className="character-list-toolbar">
            <span>
              {data.characters.length}{' '}
              {data.characters.length === 1 ? 'character' : 'characters'}
            </span>

            <button
              className="text-button"
              type="button"
              onClick={() => void loadCharacters()}
              disabled={loading || deletingId !== null}
            >
              ↻ Refresh
            </button>
          </div>

          <div className="character-grid">
            {data.characters.map((character) => (
              <CharacterCard
                key={character.id}
                character={character}
                playerName={
                  playerNames.get(character.player_id) ?? 'Unknown player'
                }
                editionName={
                  editionNames.get(character.edition_id) ?? 'Unknown edition'
                }
                speciesName={
                  character.species_id
                    ? speciesNames.get(character.species_id) ?? 'Unknown species'
                    : 'Not selected'
                }
                backgroundName={
                  character.background_id
                    ? backgroundNames.get(character.background_id) ?? 'Unknown background'
                    : 'Not selected'
                }
                onDelete={(id) => void handleDelete(id)}
              />
            ))}
          </div>
        </>
      )}
    </section>
  )
}
