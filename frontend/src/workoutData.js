const blankSeriesValues = {
  reps: 0,
  load_kg: 0,
  duration_seconds: 0,
  difficulty: 5,
  assistance_kg: 0,
};

export function blankSeries(overrides = {}) {
  return {...blankSeriesValues, ...overrides};
}

export function blankExercise(overrides = {}) {
  return {
    exercise: '',
    category: 'autre',
    notes: '',
    series: [blankSeries()],
    ...overrides,
  };
}

export function newWorkout() {
  return {
    title: '',
    date: new Date().toISOString().slice(0, 10),
    type: 'Skill',
    intensity: 7,
    duration_minutes: 60,
    notes: '',
    exercises: [blankExercise()],
  };
}

export function groupWorkoutSets(sets = []) {
  const groups = [];
  const byExercise = new Map();

  for (const set of sets) {
    const key = JSON.stringify([set.exercise, set.category || 'autre', set.notes || '']);
    let group = byExercise.get(key);
    if (!group) {
      group = blankExercise({
        exercise: set.exercise || '',
        category: set.category || 'autre',
        notes: set.notes || '',
        series: [],
      });
      byExercise.set(key, group);
      groups.push(group);
    }
    const copies = Math.max(1, Number(set.set_count) || 1);
    for (let index = 0; index < copies; index += 1) {
      group.series.push(blankSeries({
        reps: Number(set.reps) || 0,
        load_kg: Number(set.load_kg) || 0,
        duration_seconds: Number(set.duration_seconds) || 0,
        difficulty: Number(set.difficulty) || 5,
        assistance_kg: Number(set.assistance_kg) || 0,
      }));
    }
  }
  return groups;
}

export function editableWorkout(workout) {
  if (!workout) return newWorkout();
  const exercises = groupWorkoutSets(workout.sets);
  return {
    title: workout.title,
    date: workout.date,
    type: workout.type,
    intensity: workout.intensity,
    duration_minutes: workout.duration_minutes,
    notes: workout.notes || '',
    exercises: exercises.length ? exercises : [blankExercise()],
  };
}

export function workoutPayload(form) {
  return {
    title: form.title.trim(),
    date: form.date,
    type: form.type,
    intensity: Number(form.intensity),
    duration_minutes: Number(form.duration_minutes),
    notes: form.notes.trim(),
    sets: form.exercises.flatMap((exercise) => exercise.series.map((series) => ({
      exercise: exercise.exercise.trim(),
      category: exercise.category.trim() || 'autre',
      set_count: 1,
      reps: Number(series.reps) || 0,
      load_kg: Number(series.load_kg) || 0,
      duration_seconds: Number(series.duration_seconds) || 0,
      difficulty: Number(series.difficulty),
      assistance_kg: Number(series.assistance_kg) || 0,
      notes: exercise.notes.trim(),
    }))),
  };
}
