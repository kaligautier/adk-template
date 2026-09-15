"""Instructions Manager - Load and render instructions from Jinja2 templates."""

import logging

import frontmatter
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError, meta

from app.utils.error import InstructionError

logger = logging.getLogger(__name__)


class InstructionsManager:
    """Manager for loading and rendering Jinja2 instruction templates."""

    _env = None

    @classmethod
    def _get_env(cls, templates_dir: str = None):
        """Get or create Jinja2 environment."""
        if templates_dir is None:
            # Import here to avoid circular dependency
            from app.config.settings import settings

            templates_dir = settings.INSTRUCTIONS_DIR

        if cls._env is None:
            loader = FileSystemLoader(templates_dir)
            cls._env = Environment(
                loader=loader,
                undefined=StrictUndefined,
            )
        return cls._env

    @staticmethod
    def get_instructions(template, **kwargs):
        """
        Load and render an instructions template.

        Args:
            template: Template name (without .j2 extension)
            **kwargs: Variables to pass to template

        Returns:
            str: Rendered instructions

        Raises:
            InstructionError: If template loading or rendering fails
        """
        env = InstructionsManager._get_env()
        template_path = f"{template}.j2"
        logger.info(f"Loading instructions template: {template_path}")

        try:
            with open(env.loader.get_source(env, template_path)[1]) as file:
                post = frontmatter.load(file)
        except FileNotFoundError as e:
            error_msg = f"Template file not found: {template_path}"
            logger.error(error_msg)
            raise InstructionError(
                message=error_msg,
                details={"template": template, "template_path": template_path},
            ) from e
        except Exception as e:
            error_msg = f"Failed to load template: {template_path}"
            logger.error(f"{error_msg}: {str(e)}")
            raise InstructionError(
                message=error_msg,
                details={
                    "template": template,
                    "template_path": template_path,
                    "error": str(e),
                },
            ) from e

        template_obj = env.from_string(post.content)
        try:
            rendered = template_obj.render(**kwargs)
            var_count = len(kwargs)
            logger.debug(
                f"Successfully rendered instructions '{template_path}' "
                f"with {var_count} variables"
            )
            return rendered
        except TemplateError as e:
            error_msg = f"Error rendering template '{template_path}'"
            logger.error(f"{error_msg}: {str(e)}")
            raise InstructionError(
                message=error_msg,
                details={
                    "template": template,
                    "template_path": template_path,
                    "variables": list(kwargs.keys()),
                    "error": str(e),
                },
            ) from e

    @staticmethod
    def get_template_info(template):
        """
        Get template metadata and variables.

        Args:
            template: Template name (without .j2 extension)

        Returns:
            dict: Template information including frontmatter and variables

        Raises:
            InstructionError: If template loading fails
        """
        env = InstructionsManager._get_env()
        template_path = f"{template}.j2"
        logger.info(f"Getting template info for: {template_path}")

        try:
            with open(env.loader.get_source(env, template_path)[1]) as file:
                post = frontmatter.load(file)
        except FileNotFoundError as e:
            error_msg = f"Template file not found: {template_path}"
            logger.error(error_msg)
            raise InstructionError(
                message=error_msg,
                details={"template": template, "template_path": template_path},
            ) from e
        except Exception as e:
            error_msg = f"Failed to load template: {template_path}"
            logger.error(f"{error_msg}: {str(e)}")
            raise InstructionError(
                message=error_msg,
                details={
                    "template": template,
                    "template_path": template_path,
                    "error": str(e),
                },
            ) from e

        try:
            ast = env.parse(post.content)
            variables = meta.find_undeclared_variables(ast)
        except Exception as e:
            error_msg = f"Failed to parse template: {template_path}"
            logger.error(f"{error_msg}: {str(e)}")
            raise InstructionError(
                message=error_msg,
                details={
                    "template": template,
                    "template_path": template_path,
                    "error": str(e),
                },
            ) from e

        info = {
            "name": template,
            "description": post.metadata.get("description", "No description provided"),
            "author": post.metadata.get("author", "Unknown"),
            "variables": list(variables),
            "frontmatter": post.metadata,
        }

        logger.debug(
            f"Template '{template_path}' has {len(variables)} variables: "
            f"{', '.join(variables)}"
        )

        return info
