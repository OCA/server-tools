Base recursive model
====================

Create two abstract model which can be used to manage recursive relations
-------------------------------------------------------------------------
    * Easily create recursive model (instead of having to create parent_id
        each time, you now just have to inherit the abstract model
    * Define configuration fields which can then be inherited and overridden
        by children and children models. You have use example with modules
        vote and project_assignment.