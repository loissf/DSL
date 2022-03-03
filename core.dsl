class Trigger:
    var funct = void
    var condition = void
    var event_type = void

    function Trigger(funct, condition, type):
        this.funct = funct
        this.condition = condition
        this.event_type = type
    end
end

class Message:
    var content = void
    var author = void
    var context = void

    function Message(content, author, context):
        this.content = content
        this.author = author
        this.context = context
    end
end

# class Trigger: var funct = void, var condition = void, var event_type = void, function Trigger(funct, condition, type): this.funct = funct, this.condition = condition, this.event_type = type end end
# class Message: var content = void, var author = void, var context = void, function Message(content, author, context): this.content = content, this.author = author, this.context = context end end
