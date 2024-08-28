import os
import time
from typing import Dict, List

from huggingface_hub import HfApi, create_collection, list_collections, add_collection_item, delete_collection, metadata_update
from tqdm import tqdm

from masa_tools.qc.logging_config import Logger
from masa_tools.qc.error_handler import ErrorHandler

class HuggingFaceManager:
    """
    A class for managing Hugging Face datasets and collections.

    This class provides methods for interacting with the Hugging Face API to manage datasets and collections.
    It includes functionality for creating and deleting collections, uploading datasets, and updating dataset metadata.

    Attributes:
        org_name (str): The name of the Hugging Face organization.
        token (str): The Hugging Face API token for authentication.
        api (HfApi): An instance of the Hugging Face API client.
        logger (Logger): An instance of the Logger class for logging messages.
        error_handler (ErrorHandler): An instance of the ErrorHandler class for handling errors.
    """

    def __init__(self, org_name: str, token: str):
        """
        Initialize the HuggingFaceManager with the organization name and API token.

        Args:
            org_name (str): The name of the Hugging Face organization.
            token (str): The Hugging Face API token for authentication.
        """
        self.org_name = org_name
        self.token = token
        self.api = HfApi()
        self.logger = Logger()
        self.error_handler = ErrorHandler()

    @property
    def datasets(self) -> List[str]:
        """
        Get a list of datasets associated with the organization.

        Returns:
            List[str]: A list of dataset names.
        """
        return self.api.list_datasets(author=self.org_name)

    def get_or_create_collection(self, collection_name: str) -> str:
        """
        Get or create a collection with the specified name.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            str: The slug of the collection.
        """
        try:
            self.logger.log_info(f"Checking for existing collection: {collection_name}", context="HuggingFaceManager")
            collections = list_collections(owner=self.org_name)
            for collection in collections:
                if collection.title == collection_name:
                    self.logger.log_info(f"Found existing collection: {collection_name}", context="HuggingFaceManager")
                    return collection.slug
            
            self.logger.log_info(f"Creating new collection: {collection_name}", context="HuggingFaceManager")
            collection = create_collection(
                title=collection_name,
                namespace=self.org_name,
                description=f"Collection for {collection_name}",
                private=False
            )
            self.logger.log_info(f"Created new collection: {collection_name}", context="HuggingFaceManager")
            return collection.slug
        except Exception as e:
            self.error_handler.handle_error(self.get_or_create_collection)(e)

    def upload_dataset(self, dataset, repo_id: str, collection_slug: str, file_path: str, file_mod_time: float, hf_upload_record: Dict[str, float]):
        """
        Upload a dataset to Hugging Face and add it to a collection.

        Args:
            dataset: The dataset object to upload.
            repo_id (str): The repository ID for the dataset.
            collection_slug (str): The slug of the collection to add the dataset to.
            file_path (str): The path of the file associated with the dataset.
            file_mod_time (float): The modification time of the file.
            hf_upload_record (Dict[str, float]): A dictionary to record the upload information.
        """
        dataset.push_to_hub(repo_id=repo_id)
        add_collection_item(
            collection_slug=collection_slug,
            item_id=repo_id,
            item_type="dataset",
            exists_ok=True
        )
        self.logger.log_info(f"Successfully uploaded {file_path} to {collection_slug}", context="HuggingFaceManager")
        hf_upload_record[file_path] = file_mod_time
        time.sleep(5)  # Sleep for 5 seconds to avoid overloading the API

    def repo_exists(self, repo_id: str) -> bool:
        """
        Check if a repository exists on Hugging Face.

        Args:
            repo_id (str): The repository ID to check.

        Returns:
            bool: True if the repository exists, False otherwise.
        """
        try:
            self.api.repo_info(repo_id=repo_id)
            self.logger.log_info(f"Repository {repo_id} already exists. Skipping upload.", context="HuggingFaceManager")
            return True
        except Exception as e:
            if "404 Client Error" in str(e):
                return False
            else:
                self.error_handler.handle_error(self.repo_exists)(e)

    def delete_collection_by_slug(self):
        """
        Delete a collection by selecting its slug from a list of collections.

        This method prompts the user to select a collection to delete from a list of collections
        associated with the organization. It provides options to delete a specific collection or
        all collections. The user is prompted for confirmation before deleting any collections.
        """
        try:
            collections = list_collections(owner=self.org_name)
            if not collections:
                self.logger.log_info(f"No collections found for organization: {self.org_name}", context="HuggingFaceManager")
                return

            print(f"Collections for organization: {self.org_name}")
            for idx, collection in enumerate(collections, start=1):
                print(f"{idx}. {collection.title}")
            print(f"{len(collections) + 1}. All collections")

            print("Select a collection to delete:")
            for idx, collection in enumerate(collections, start=1):
                print(f"{idx}. {collection.title} (slug: {collection.slug})")
            print(f"{len(collections) + 1}. All collections")

            choice = int(input("Enter the number of the collection to delete: "))
            if choice == len(collections) + 1:
                confirm = input("Are you sure you want to delete all collections? (yes/no): ")
                if confirm.lower() == 'yes':
                    for collection in collections:
                        self.logger.log_info(f"Deleting collection: {collection.slug}", context="HuggingFaceManager")
                        delete_collection(collection_slug=collection.slug, missing_ok=True)
                        self.logger.log_info(f"Successfully deleted collection: {collection.slug}", context="HuggingFaceManager")
                else:
                    self.logger.log_info("Deletion of all collections cancelled.", context="HuggingFaceManager")
            elif 1 <= choice <= len(collections):
                collection_slug = collections[choice - 1].slug
                confirm = input(f"Are you sure you want to delete the collection {collection_slug}? (yes/no): ")
                if confirm.lower() == 'yes':
                    self.logger.log_info(f"Deleting collection: {collection_slug}", context="HuggingFaceManager")
                    delete_collection(collection_slug=collection_slug, missing_ok=True)
                    self.logger.log_info(f"Successfully deleted collection: {collection_slug}", context="HuggingFaceManager")
                else:
                    self.logger.log_info(f"Deletion of collection {collection_slug} cancelled.", context="HuggingFaceManager")
            else:
                self.logger.log_error("Invalid choice.", context="HuggingFaceManager")
        except Exception as e:
            self.error_handler.handle_error(self.delete_collection_by_slug)(e)

    def delete_datasets(self):
        """
        Delete all datasets associated with the organization.

        This method prompts the user for confirmation before deleting all datasets associated with
        the organization. If confirmed, it iterates over the datasets and deletes each one using
        the Hugging Face API. It logs the progress and handles any exceptions that occur during
        the deletion process.
        """
        try:
            self.logger.log_info(f"Deleting {len(self.datasets)} datasets for organization: {self.org_name}", context="HuggingFaceManager")
            
            confirm = input(f"Are you sure you want to delete all {len(self.datasets)} datasets? (yes/no): ")
            if confirm.lower() == 'yes':
                for dataset_name in tqdm(self.datasets, desc="Deleting datasets"):
                    try:
                        self.api.delete_repo(
                            repo_id=f"{dataset_name}",
                            token=self.token,
                            repo_type="dataset",
                            missing_ok=True
                        )
                        self.logger.log_info(f"Successfully deleted dataset: {dataset_name} from organization: {self.org_name}", context="HuggingFaceManager")
                        time.sleep(2)  # Sleep for the specified delay to avoid overloading the API
                    except Exception as e:
                        self.error_handler.handle_error(self.delete_datasets)(e)
            else:
                self.logger.log_info("Deletion of all datasets cancelled.", context="HuggingFaceManager")
        except Exception as e:
            self.error_handler.handle_error(self.delete_datasets)(e)

    def update_dataset_cards(self):
        """
        Update the metadata of all datasets associated with the organization.

        This method updates the metadata of all datasets associated with the organization. It
        iterates over the datasets and updates the metadata using the Hugging Face API. The
        updated metadata includes fields such as data source, language, and tags. It logs the
        progress and handles any exceptions that occur during the update process.
        """
        try:
            self.logger.log_info(f"Updating dataset cards for organization: {self.org_name}", context="HuggingFaceManager")
            
            for dataset in tqdm(self.datasets, desc="Updating dataset cards"):
                repo_id = dataset.id
                
                # Prepare the new metadata
                new_metadata = {
                    "data_source": "",  # Example: set license to Apache-2.0
                    "language": ["en"],  # Example: set language to English
                    "tags": ["transcript", "podcast"],  # Example: add tags
                    # Add more fields as needed
                }
                
                # Update the metadata
                url = metadata_update(
                    repo_id=repo_id,
                    metadata=new_metadata,
                    repo_type="dataset",
                    token=self.token
                )
                
                self.logger.log_info(f"Updated metadata for dataset: {repo_id}", context="HuggingFaceManager")
                self.logger.log_info(f"Updated metadata URL: {url}", context="HuggingFaceManager")
                time.sleep(1)  # Sleep to avoid rate limiting
            
            self.logger.log_info(f"Finished updating metadata for {len(self.datasets)} datasets", context="HuggingFaceManager")

        except Exception as e:
            self.error_handler.handle_error(self.update_dataset_cards)(e)
