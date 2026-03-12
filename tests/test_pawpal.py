import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from pawpal_system import Task, Pet, Owner


class TestTaskCompletion:
    """Tests for Task.mark_complete() functionality."""
    
    def test_task_initially_not_completed(self):
        """Verify that a newly created task is not completed."""
        task = Task("Feed the dog", 1.0, 1, "feeding", "Give dog kibble")
        assert task.is_completed() == False
    
    def test_mark_complete_changes_status_to_true(self):
        """Verify that calling mark_complete() changes the task's status to completed."""
        task = Task("Feed the dog", 1.0, 1, "feeding", "Give dog kibble")
        task.mark_complete()
        assert task.is_completed() == True
    
    def test_mark_complete_reflects_change(self):
        """Verify that is_completed() reflects the change after mark_complete()."""
        task = Task("Groom the cat", 2.0, 2, "grooming", "Brush cat's fur")
        assert task.is_completed() == False
        task.mark_complete()
        assert task.is_completed() == True
    
    def test_multiple_tasks_completion_independent(self):
        """Verify that marking one task complete doesn't affect others."""
        task1 = Task("Feed", 1.0, 1, "feeding")
        task2 = Task("Walk", 0.5, 2, "exercise")
        
        task1.mark_complete()
        
        assert task1.is_completed() == True
        assert task2.is_completed() == False


class TestTaskAdditionToPet:
    """Tests for Pet.add_task() and task count functionality."""
    
    def test_pet_initially_no_tasks(self):
        """Verify that a newly created pet has no tasks."""
        pet = Pet("Buddy", "Dog", "Golden Retriever", 3.5)
        assert len(pet.get_tasks()) == 0
    
    def test_add_single_task_increases_count(self):
        """Verify that adding a task to a pet increases the task count by 1."""
        pet = Pet("Buddy", "Dog", "Golden Retriever", 3.5)
        task = Task("Feed", 1.0, 1, "feeding")
        
        initial_count = len(pet.get_tasks())
        pet.add_task(task)
        final_count = len(pet.get_tasks())
        
        assert final_count == initial_count + 1
    
    def test_add_multiple_tasks_increases_count(self):
        """Verify that adding multiple tasks increases the task count correctly."""
        pet = Pet("Whiskers", "Cat", "Persian", 5.0)
        task1 = Task("Feed", 1.0, 1, "feeding")
        task2 = Task("Groom", 2.0, 2, "grooming")
        task3 = Task("Play", 0.5, 3, "exercise")
        
        assert len(pet.get_tasks()) == 0
        
        pet.add_task(task1)
        assert len(pet.get_tasks()) == 1
        
        pet.add_task(task2)
        assert len(pet.get_tasks()) == 2
        
        pet.add_task(task3)
        assert len(pet.get_tasks()) == 3
    
    def test_added_task_is_in_pet_tasks(self):
        """Verify that an added task is actually present in the pet's task list."""
        pet = Pet("Max", "Dog", "Labrador", 2.0)
        task = Task("Walk", 0.5, 1, "exercise")
        
        pet.add_task(task)
        tasks = pet.get_tasks()
        
        assert task in tasks
        assert len(tasks) == 1
    
    def test_add_duplicate_task_does_not_increase_count(self):
        """Verify that adding the same task twice doesn't increase the count twice."""
        pet = Pet("Rex", "Dog", "Boxer", 4.0)
        task = Task("Train", 1.0, 2, "training")
        
        pet.add_task(task)
        initial_count = len(pet.get_tasks())
        
        # Try to add the same task again
        pet.add_task(task)
        final_count = len(pet.get_tasks())
        
        assert final_count == initial_count


class TestIntegrationTaskCompletion:
    """Integration tests combining task completion and pet task management."""
    
    def test_complete_task_assigned_to_pet(self):
        """Verify that a task assigned to a pet can be marked as completed."""
        pet = Pet("Fluffy", "Cat", "Siamese", 3.0)
        task = Task("Brush teeth", 0.5, 3, "grooming")
        
        pet.add_task(task)
        task.mark_complete()
        
        assert task.is_completed() == True
        assert task in pet.get_tasks()
    
    def test_pet_task_count_unchanged_after_completion(self):
        """Verify that completing a task doesn't affect the pet's task count."""
        pet = Pet("Spot", "Dog", "Dalmatian", 2.5)
        task1 = Task("Feed", 1.0, 1, "feeding")
        task2 = Task("Walk", 0.5, 2, "exercise")
        
        pet.add_task(task1)
        pet.add_task(task2)
        initial_count = len(pet.get_tasks())
        
        task1.mark_complete()
        
        assert len(pet.get_tasks()) == initial_count
