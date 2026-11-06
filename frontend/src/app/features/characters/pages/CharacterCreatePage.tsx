import { useEffect, useState, type FormEvent } from 'react'

import { createCharacter } from '../services/characterService'
import {
  getBackgrounds,
  getEditions,
  getPlayers,
  getSpecies,
  getSpeciesVariants,
} from '../services/referenceDataService'

import type { CharacterCreate } from '../types/character'
import type {
  BackgroundOption,
  EditionOption,
  PlayerOption,
  SpeciesOption,
  SpeciesVariantOption,
} from '../types/referenceData'

interface CharacterCreatePageProps {
  onCancel: () => void
  onCreated: () => void
}

export default function CharacterCreatePage({
  onCancel,
  onCreated,
}: CharacterCreatePageProps) {
  const [players, setPlayers] = useState<PlayerOption[]>([])
  const [editions, setEditions] = useState<EditionOption[]>([])
  const [species, setSpecies] = useState<SpeciesOption[]>([])
  const [variants, setVariants] = useState<SpeciesVariantOption[]>([])
  const [backgrounds, setBackgrounds] = useState<BackgroundOption[]>([])

  const [name, setName] = useState('')
  const [playerId, setPlayerId] = useState('')
  const [editionId, setEditionId] = useState('')
  const [speciesId, setSpeciesId] = useState('')
  const [variantId, setVariantId] = useState('')
  const [backgroundId, setBackgroundId] = useState('')
  const [level, setLevel] = useState('1')
  const [experiencePoints, setExperiencePoints] = useState('0')

  const [loadingReferences, setLoadingReferences] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadInitialOptions() {
      try {
        const [
          playerOptions,
          editionOptions,
          speciesOptions,
          backgroundOptions,
        ] = await Promise.all([
          getPlayers(),
          getEditions(),
          getSpecies(),
          getBackgrounds(),
        ])

        if (active) {
          setPlayers(playerOptions)
          setEditions(editionOptions)
          setSpecies(speciesOptions)
          setBackgrounds(backgroundOptions)
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load character options.',
          )
        }
      } finally {
        if (active) {
          setLoadingReferences(false)
        }
      }
    }

    void loadInitialOptions()

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    let active = true

    async function loadVariants() {
      if (!speciesId) {
        setVariants([])
        return
      }

      try {
        const options = await getSpeciesVariants(Number(speciesId))

        if (active) {
          setVariants(options)
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load species variants.',
          )
        }
      }
    }

    void loadVariants()

    return () => {
      active = false
    }
  }, [speciesId])

  function handleEditionChange(value: string) {
    setEditionId(value)
    setError(null)
  }

  function handleSpeciesChange(value: string) {
    setSpeciesId(value)
    setVariantId('')
    setError(null)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const payload: CharacterCreate = {
      name: name.trim(),
      player_id: Number(playerId),
      edition_id: Number(editionId),
      species_id: speciesId ? Number(speciesId) : null,
      species_variant_id: variantId ? Number(variantId) : null,
      background_id: backgroundId ? Number(backgroundId) : null,
      level: Number(level),
      experience_points: Number(experiencePoints),
    }

    setSaving(true)

    try {
      await createCharacter(payload)
      onCreated()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to create character.',
      )
    } finally {
      setSaving(false)
    }
  }

  if (loadingReferences) {
    return (
      <section className="characters-page">
        <div className="character-state">
          <div className="loading-symbol" aria-hidden="true">✧</div>
          <p>Preparing character options...</p>
        </div>
      </section>
    )
  }

  return (
    <section className="characters-page">
      <div className="characters-page-heading">
        <div>
          <div className="eyebrow">FORGE A NEW ADVENTURER</div>
          <h1>Create Character</h1>
          <p>Begin with the identity and origins of your new hero.</p>
        </div>
      </div>

      {error && (
        <div className="character-error" role="alert">
          {error}
        </div>
      )}

      {players.length === 0 && (
        <div className="character-notice" role="status">
          No players are available. Create a player before creating a
          character.
        </div>
      )}

      {editions.length === 0 && (
        <div className="character-notice" role="status">
          No D&D editions are available.
        </div>
      )}

      <form className="character-form" onSubmit={handleSubmit}>
        <div className="character-form-section">
          <div className="eyebrow">IDENTITY</div>
          <h2>Who is your adventurer?</h2>

          <div className="character-form-grid">
            <label className="character-field character-field-full">
              <span>Character name *</span>
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                maxLength={120}
                placeholder="Enter a character name"
                required
              />
            </label>

            <label className="character-field">
              <span>Player *</span>
              <select
                value={playerId}
                onChange={(event) => setPlayerId(event.target.value)}
                required
              >
                <option value="">Select a player</option>
                {players.map((player) => (
                  <option key={player.id} value={player.id}>
                    {player.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="character-field">
              <span>D&D edition *</span>
              <select
                value={editionId}
                onChange={(event) => handleEditionChange(event.target.value)}
                required
              >
                <option value="">Select an edition</option>
                {editions.map((edition) => (
                  <option key={edition.id} value={edition.id}>
                    {edition.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <div className="character-form-section">
          <div className="eyebrow">ORIGINS</div>
          <h2>Where does your hero come from?</h2>

          <div className="character-form-grid">
            <label className="character-field">
              <span>Species</span>
              <select
                value={speciesId}
                onChange={(event) => handleSpeciesChange(event.target.value)}
              >
                <option value="">Select a species (optional)</option>
                {species.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="character-field">
              <span>Species variant</span>
              <select
                value={variantId}
                onChange={(event) => setVariantId(event.target.value)}
                disabled={!speciesId}
              >
                <option value="">Select a variant (optional)</option>
                {variants.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="character-field character-field-full">
              <span>Background</span>
              <select
                value={backgroundId}
                onChange={(event) => setBackgroundId(event.target.value)}
              >
                <option value="">Select a background (optional)</option>
                {backgrounds.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

        </div>

        <div className="character-form-section">
          <div className="eyebrow">PROGRESSION</div>
          <h2>Starting experience</h2>

          <div className="character-form-grid">
            <label className="character-field">
              <span>Level</span>
              <input
                type="number"
                min="1"
                max="20"
                value={level}
                onChange={(event) => setLevel(event.target.value)}
                required
              />
            </label>

            <label className="character-field">
              <span>Experience points</span>
              <input
                type="number"
                min="0"
                step="1"
                value={experiencePoints}
                onChange={(event) => setExperiencePoints(event.target.value)}
                required
              />
            </label>
          </div>
        </div>

        <div className="character-form-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={onCancel}
            disabled={saving}
          >
            Cancel
          </button>

          <button
            className="primary-button"
            type="submit"
            disabled={
              saving ||
              players.length === 0 ||
              editions.length === 0
            }
          >
            {saving ? 'Creating character...' : 'Create character'}
          </button>
        </div>
      </form>
    </section>
  )
}
